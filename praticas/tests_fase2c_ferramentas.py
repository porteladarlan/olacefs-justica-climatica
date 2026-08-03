import hashlib
import importlib
import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, migrations, transaction
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import translation

from praticas.management.commands.importar_ferramentas_fase2c import (
    Command as ImportarFerramentasCommand,
)
from praticas.models import (
    Ferramenta,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    Setor,
)
from praticas.views import ferramentas_catalogadas


class FerramentaModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setor = Setor.objects.create(
            nome="Energia",
            nome_es="Energía",
            nome_en="Energy",
        )

    def criar_ferramenta(self, **alteracoes):
        dados = {
            "codigo": "ferramenta-modelo",
            "titulo_es": "Herramienta canónica",
            "descricao_es": "Descripción institucional en español.",
            "responsavel": "Institución responsable",
            "periodo": "2025",
            "setor": self.setor,
            "url": "https://example.org/herramienta",
            "situacao": Ferramenta.Situacao.PUBLICADA,
            "ordem": 1,
        }
        dados.update(alteracoes)
        return Ferramenta.objects.create(**dados)

    def test_fallback_para_espanhol_quando_traducao_institucional_nao_existe(self):
        ferramenta = self.criar_ferramenta()

        for idioma in ("pt-br", "es", "en"):
            with self.subTest(idioma=idioma), translation.override(idioma):
                self.assertEqual(ferramenta.titulo_exibicao, "Herramienta canónica")
                self.assertEqual(
                    ferramenta.descricao_exibicao,
                    "Descripción institucional en español.",
                )

    def test_traducao_institucional_prevalece_quando_disponivel(self):
        ferramenta = self.criar_ferramenta(
            titulo="Ferramenta institucional",
            titulo_en="Institutional tool",
            descricao="Descrição institucional.",
            descricao_en="Institutional description.",
        )

        with translation.override("pt-br"):
            self.assertEqual(ferramenta.titulo_exibicao, "Ferramenta institucional")
        with translation.override("en"):
            self.assertEqual(ferramenta.titulo_exibicao, "Institutional tool")

    def test_catalogo_publica_somente_situacao_publicada(self):
        publicada = self.criar_ferramenta()
        self.criar_ferramenta(
            codigo="ferramenta-rascunho",
            situacao=Ferramenta.Situacao.RASCUNHO,
            ordem=2,
        )

        self.assertQuerySetEqual(ferramentas_catalogadas(), [publicada])

    def test_ordem_e_unica(self):
        self.criar_ferramenta()

        with self.assertRaises(IntegrityError), transaction.atomic():
            self.criar_ferramenta(codigo="outra-ferramenta")

    def test_migration_da_fase2c_e_somente_estrutural(self):
        modulo = importlib.import_module("praticas.migrations.0012_fase2c_ferramenta")

        self.assertFalse(
            any(
                isinstance(operacao, (migrations.RunPython, migrations.RunSQL))
                for operacao in modulo.Migration.operations
            )
        )


class FerramentasCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setor_energia = Setor.objects.create(
            nome="Energia",
            nome_es="Energía",
            nome_en="Energy",
        )
        cls.setor_agua = Setor.objects.create(
            nome="Agua y saneamiento",
            nome_es="Agua y saneamiento",
        )
        cls.publicada = Ferramenta.objects.create(
            codigo="climate-scanner",
            titulo_es="Climate Scanner",
            descricao_es="Herramienta global de evaluación rápida.",
            responsavel="INTOSAI WGEA + TCU Brasil",
            periodo="2022–2025",
            setor=cls.setor_energia,
            url="https://example.org/climate-scanner",
            situacao=Ferramenta.Situacao.PUBLICADA,
            ordem=1,
        )
        cls.publicada_agua = Ferramenta.objects.create(
            codigo="auditoria-agua",
            titulo_es="Auditoría Coordinada sobre Recursos Hídricos",
            descricao_es="Referencia metodológica para auditar agua y saneamiento.",
            responsavel="COMTEMA / OLACEFS",
            periodo="2014",
            setor=cls.setor_agua,
            url="https://example.org/agua",
            situacao=Ferramenta.Situacao.PUBLICADA,
            ordem=2,
        )
        cls.rascunho = Ferramenta.objects.create(
            codigo="nao-publicada",
            titulo_es="Contenido no publicado",
            descricao_es="No debe aparecer.",
            responsavel="Curaduría",
            periodo="2026",
            setor=cls.setor_energia,
            url="https://example.org/rascunho",
            situacao=Ferramenta.Situacao.RASCUNHO,
            ordem=3,
        )

    def test_interface_oficial_e_fallback_sao_trilingues(self):
        casos = (
            (
                "/ferramentas/",
                "Caixa de ferramentas",
                "Ferramentas para auditorias de justiça climática",
                "Buscar ferramenta…",
                "Todas",
                "ferramentas encontradas",
            ),
            (
                "/es/ferramentas/",
                "Caja de herramientas",
                "Herramientas para auditorías de justicia climática",
                "Buscar herramienta…",
                "Todos",
                "herramientas encontradas",
            ),
            (
                "/en/ferramentas/",
                "Toolbox",
                "Tools for climate-justice audits",
                "Search tool…",
                "All",
                "tools found",
            ),
        )
        for caminho, eyebrow, titulo, busca, geral, contador in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, eyebrow)
                self.assertContains(response, titulo)
                self.assertContains(response, busca)
                self.assertContains(response, geral)
                self.assertContains(response, contador)
                self.assertContains(response, "Climate Scanner")
                self.assertContains(response, "INTOSAI WGEA + TCU Brasil")
                self.assertNotContains(response, self.rascunho.titulo_es)
                self.assertNotContains(response, "catalog is being prepared")

    def test_busca_progressiva_nao_exibe_botao_separado(self):
        response = self.client.get(reverse("ferramentas"))
        script = Path(
            finders.find("praticas/js/ferramentas-publicas.js")
        ).read_text(encoding="utf-8")

        self.assertContains(response, "data-tools-progressive-search")
        self.assertContains(response, "ferramentas-publicas.")
        self.assertNotContains(response, '<button class="btn btn-primary')
        self.assertNotContains(response, ">Buscar<")
        self.assertIn("window.fetch", script)
        self.assertIn("window.history.replaceState", script)
        self.assertNotIn("requestSubmit", script)

    def test_busca_considera_titulo_descricao_responsavel_setor_e_periodo(self):
        for termo in (
            "Climate Scanner",
            "evaluación rápida",
            "INTOSAI WGEA",
            "Energía",
            "2022–2025",
        ):
            with self.subTest(termo=termo):
                response = self.client.get(reverse("ferramentas"), {"q": termo})
                self.assertEqual(response.context["total_resultados"], 1)
                self.assertContains(response, self.publicada.titulo_es)
                self.assertNotContains(response, self.publicada_agua.titulo_es)

    def test_filtro_por_setor_e_contador_singular(self):
        response = self.client.get(
            reverse("ferramentas"),
            {"setor": self.setor_agua.pk},
        )

        self.assertEqual(response.context["total_resultados"], 1)
        self.assertContains(response, "ferramenta encontrada")
        self.assertContains(response, self.publicada_agua.titulo_es)
        self.assertNotContains(response, self.publicada.titulo_es)

    def test_busca_sem_resultados_nao_e_confundida_com_catalogo_em_preparacao(self):
        response = self.client.get(reverse("ferramentas"), {"q": "inexistente"})

        self.assertEqual(response.context["total_publicadas"], 2)
        self.assertEqual(response.context["total_resultados"], 0)
        self.assertContains(
            response,
            "Nenhum resultado encontrado. Tente ampliar a busca ou limpar os filtros.",
        )
        self.assertNotContains(response, "O catálogo de ferramentas está em preparação.")

    def test_estado_de_preparacao_aparece_somente_sem_publicadas(self):
        Ferramenta.objects.update(situacao=Ferramenta.Situacao.RASCUNHO)

        response = self.client.get(reverse("ferramentas"))

        self.assertEqual(response.context["total_publicadas"], 0)
        self.assertContains(
            response,
            "O cat&aacute;logo de ferramentas est&aacute; em prepara&ccedil;&atilde;o.",
            html=False,
        )
        self.assertNotContains(response, "data-tools-filter-form")

    def test_links_externos_sao_seguros_e_icones_nao_vazam_como_texto(self):
        response = self.client.get(reverse("ferramentas"))

        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        for nome_icone in ("construction", "search", "north_east", "search_off"):
            self.assertNotContains(response, f">{nome_icone}<")


class ImportarFerramentasFase2CTests(TransactionTestCase):
    reset_sequences = True

    TITULOS_OFICIAIS = (
        "Climate Scanner",
        "Auditoría Cooperativa Global de Adaptación al Cambio Climático",
        "Guía sobre Auditoría Ambiental",
        "Referencial para Evaluación de la Gobernanza en Políticas Públicas",
        "Auditoría Coordinada sobre Recursos Hídricos",
        "Guía Práctica de Auditoría para la Transición Energética",
        (
            "Auditoría Coordinada sobre Preparación para la Implementación de los ODS "
            "con foco en la Meta 2.4 - Producción sostenible de alimentos"
        ),
        "Auditoría Coordinada en Áreas Protegidas",
        "Auditing Biodiversity: Guidance for Supreme Audit Institutions",
        "GUID 5330 – Orientaciones sobre la Auditoría de la Gestión de Desastres",
        (
            "Fiscalización Superior en México y la Región Latinoamericana para la "
            "Prevención de Desastres"
        ),
        "EI Auditors' Toolkit – Extractive Industries Auditor Toolkit",
        "Auditoría Coordinada de Pasivos Ambientales Mineros",
        (
            "Géner.A / IMPGAI – Instrumento de Medición de la Perspectiva de Género "
            "en el Ámbito Institucional"
        ),
        (
            "IMPGPP – Instrumento de Medición de la Perspectiva de Género en "
            "Políticas Públicas"
        ),
    )

    SETORES = (
        "Agua y saneamiento",
        "Alimentación y agricultura",
        "Bosques, biodiversidad y ecosistemas",
        "Energía",
        "Gestión de riesgo y desastres",
        "Industria extractiva y minería",
        "Transversal",
        "Transversal – Género",
    )

    def setUp(self):
        self.executor = get_user_model().objects.create_user(
            username="executor-fase2c",
            password="senha-de-teste",
            is_staff=True,
        )
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio_temporario.cleanup)

    def ferramentas_fonte(self):
        ferramentas = []
        for ordem, titulo in enumerate(self.TITULOS_OFICIAIS, start=1):
            ferramentas.append(
                {
                    "sector": self.SETORES[(ordem - 1) % len(self.SETORES)],
                    "nombre": titulo,
                    "responsable": f"Institución responsable {ordem}",
                    "ano": "2025" if ordem % 2 else "2022–2025",
                    "desc": f"Descripción oficial sin reescritura {ordem}.",
                    "link": f"https://example.org/herramienta-{ordem}",
                }
            )
        return ferramentas

    def criar_fonte(self, ferramentas=None):
        dados = {"herramientas": ferramentas or self.ferramentas_fonte()}
        conteudo = (
            "<!doctype html><script>window.PJC_DATA = "
            + json.dumps(dados, ensure_ascii=False)
            + ";</script>"
        )
        caminho = Path(self.diretorio_temporario.name) / "prototipo-oficial.html"
        caminho.write_text(conteudo, encoding="utf-8")
        sha256 = hashlib.sha256(caminho.read_bytes()).hexdigest()
        return caminho, sha256

    def executar(
        self,
        caminho=None,
        sha256=None,
        *,
        dry_run=False,
        publicar=False,
        atualizar=False,
        reverter_lote=None,
    ):
        argumentos = {
            "executado_por": self.executor.username,
            "stdout": StringIO(),
        }
        if caminho is not None:
            argumentos["arquivo"] = str(caminho)
        if dry_run:
            argumentos["dry_run"] = True
        if publicar:
            argumentos["publicar"] = True
        if atualizar:
            argumentos["atualizar"] = True
        if reverter_lote:
            argumentos["reverter_lote"] = str(reverter_lote)
        with mock.patch.object(
            ImportarFerramentasCommand,
            "SHA256_FONTE_OFICIAL",
            sha256 or ImportarFerramentasCommand.SHA256_FONTE_OFICIAL,
        ):
            call_command("importar_ferramentas_fase2c", **argumentos)
        return argumentos["stdout"].getvalue()

    def test_dry_run_valida_15_registros_sem_escrever_no_banco(self):
        caminho, sha256 = self.criar_fonte()

        saida = self.executar(caminho, sha256, dry_run=True)

        self.assertIn("DRY-RUN APROVADO", saida)
        self.assertIn("15 ferramentas", saida)
        self.assertIn("Criadas como rascunho: 15", saida)
        self.assertIn("publicadas: 0", saida)
        self.assertIn("atualizadas: 0", saida)
        self.assertIn("ignoradas: 0", saida)
        self.assertIn("divergências: 0", saida)
        self.assertIn(sha256, saida)
        self.assertFalse(Ferramenta.objects.exists())
        self.assertFalse(LoteImportacaoConteudo.objects.exists())

    def test_help_contem_publicar(self):
        parser = ImportarFerramentasCommand().create_parser(
            "manage.py", "importar_ferramentas_fase2c"
        )

        self.assertIn("--publicar", parser.format_help())

    def test_help_contem_atualizar(self):
        parser = ImportarFerramentasCommand().create_parser(
            "manage.py", "importar_ferramentas_fase2c"
        )

        self.assertIn("--atualizar", parser.format_help())

    def test_help_contem_reverter_lote(self):
        parser = ImportarFerramentasCommand().create_parser(
            "manage.py", "importar_ferramentas_fase2c"
        )

        self.assertIn("--reverter-lote", parser.format_help())

    def test_carga_cria_15_rascunhos_oito_setores_e_ledger_com_hashes(self):
        caminho, sha256 = self.criar_fonte()

        self.executar(caminho, sha256)

        self.assertEqual(Ferramenta.objects.count(), 15)
        self.assertEqual(Setor.objects.count(), 8)
        self.assertEqual(
            Ferramenta.objects.filter(situacao=Ferramenta.Situacao.RASCUNHO).count(),
            15,
        )
        lote = LoteImportacaoConteudo.objects.get()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.CONCLUIDO)
        self.assertEqual(lote.sha256, sha256)
        self.assertIn("db_sha256_antes", lote.relatorio_divergencias)
        self.assertEqual(lote.itens.count(), 23)
        self.assertEqual(
            lote.itens.filter(
                entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA
            ).count(),
            15,
        )
        self.assertEqual(
            lote.itens.filter(
                entidade=ItemLoteImportacaoConteudo.Entidade.SETOR
            ).count(),
            8,
        )
        primeira = Ferramenta.objects.get(ordem=1)
        self.assertEqual(primeira.titulo_es, "Climate Scanner")
        self.assertEqual(primeira.titulo, "")
        self.assertEqual(primeira.titulo_en, "")

    def test_reexecucao_sem_atualizar_nao_sobrescreve_divergencia(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.descricao_es = "Conteúdo divergente preservado."
        primeira.save(update_fields=("descricao_es", "atualizado_em"))

        self.executar(caminho, sha256)

        self.assertEqual(Ferramenta.objects.count(), 15)
        self.assertEqual(Setor.objects.count(), 8)
        self.assertEqual(LoteImportacaoConteudo.objects.count(), 2)
        segundo_lote = LoteImportacaoConteudo.objects.order_by("iniciado_em").last()
        self.assertEqual(
            segundo_lote.itens.filter(
                entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA,
                operacao=ItemLoteImportacaoConteudo.Operacao.IGNORADO,
            ).count(),
            15,
        )
        primeira.refresh_from_db()
        self.assertEqual(primeira.descricao_es, "Conteúdo divergente preservado.")
        self.assertEqual(segundo_lote.status, LoteImportacaoConteudo.Status.COM_DIVERGENCIAS)
        self.assertEqual(segundo_lote.contagens_realizadas["divergencias_pendentes"], 1)

    def test_carga_com_publicar_cria_15_publicadas(self):
        caminho, sha256 = self.criar_fonte()

        self.executar(caminho, sha256, publicar=True)

        self.assertEqual(
            Ferramenta.objects.filter(situacao=Ferramenta.Situacao.PUBLICADA).count(),
            15,
        )
        lote = LoteImportacaoConteudo.objects.get()
        self.assertEqual(lote.contagens_realizadas["ferramentas_publicadas"], 15)

    def test_publicar_sem_atualizar_ignora_registro_divergente(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeiro_lote_id = primeira.lote_origem_id
        primeira.descricao_es = "Divergência local preservada."
        primeira.save(update_fields=("descricao_es", "atualizado_em"))
        estado_anterior = {
            campo: getattr(primeira, campo)
            for campo in (
                "codigo",
                "titulo_es",
                "descricao_es",
                "responsavel",
                "periodo",
                "setor_id",
                "url",
                "ordem",
                "situacao",
                "lote_origem_id",
            )
        }

        self.executar(caminho, sha256, publicar=True)

        primeira.refresh_from_db()
        self.assertEqual(
            {
                campo: getattr(primeira, campo)
                for campo in estado_anterior
            },
            estado_anterior,
        )
        self.assertEqual(primeira.situacao, Ferramenta.Situacao.RASCUNHO)
        self.assertEqual(primeira.lote_origem_id, primeiro_lote_id)
        lote = LoteImportacaoConteudo.objects.order_by("iniciado_em").last()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.COM_DIVERGENCIAS)
        item = lote.itens.get(
            entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA,
            objeto_pk=str(primeira.pk),
        )
        self.assertEqual(item.operacao, ItemLoteImportacaoConteudo.Operacao.IGNORADO)

    def test_dry_run_nao_conta_divergente_como_publicado_sem_atualizar(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.descricao_es = "Divergência local preservada."
        primeira.save(update_fields=("descricao_es", "atualizado_em"))
        lotes_antes = LoteImportacaoConteudo.objects.count()

        saida = self.executar(caminho, sha256, dry_run=True, publicar=True)

        self.assertIn("publicadas: 14", saida)
        self.assertIn("ignoradas: 1", saida)
        self.assertIn("divergências: 1", saida)
        self.assertEqual(LoteImportacaoConteudo.objects.count(), lotes_antes)
        primeira.refresh_from_db()
        self.assertEqual(primeira.situacao, Ferramenta.Situacao.RASCUNHO)

    def test_publicar_com_atualizar_reconcilia_divergente_e_preserva_traducoes(self):
        ferramentas = self.ferramentas_fonte()
        caminho, sha256 = self.criar_fonte(ferramentas)
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.titulo = "Título institucional"
        primeira.titulo_en = "Institutional title"
        primeira.descricao = "Descrição institucional."
        primeira.descricao_en = "Institutional description."
        primeira.descricao_es = "Divergência a reconciliar."
        primeira.save()

        self.executar(caminho, sha256, publicar=True, atualizar=True)

        primeira.refresh_from_db()
        self.assertEqual(primeira.descricao_es, ferramentas[0]["desc"])
        self.assertEqual(primeira.situacao, Ferramenta.Situacao.PUBLICADA)
        self.assertEqual(primeira.titulo, "Título institucional")
        self.assertEqual(primeira.titulo_en, "Institutional title")
        self.assertEqual(primeira.descricao, "Descrição institucional.")
        self.assertEqual(primeira.descricao_en, "Institutional description.")
        item = LoteImportacaoConteudo.objects.order_by("iniciado_em").last().itens.get(
            entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA,
            objeto_pk=str(primeira.pk),
        )
        self.assertEqual(item.operacao, ItemLoteImportacaoConteudo.Operacao.ATUALIZADO)
        self.assertEqual(item.snapshot_anterior["descricao_es"], "Divergência a reconciliar.")

    def test_lote_com_divergencias_e_operacoes_reversiveis_pode_ser_revertido(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.descricao_es = "Divergência local preservada."
        primeira.save(update_fields=("descricao_es", "atualizado_em"))
        self.executar(caminho, sha256, publicar=True)
        lote = LoteImportacaoConteudo.objects.order_by("iniciado_em").last()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.COM_DIVERGENCIAS)
        self.assertEqual(
            Ferramenta.objects.filter(situacao=Ferramenta.Situacao.PUBLICADA).count(),
            14,
        )

        self.executar(reverter_lote=lote.identificador)

        lote.refresh_from_db()
        primeira.refresh_from_db()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERTIDO)
        self.assertFalse(
            Ferramenta.objects.exclude(situacao=Ferramenta.Situacao.RASCUNHO).exists()
        )
        self.assertEqual(primeira.descricao_es, "Divergência local preservada.")
        with self.assertRaisesMessage(CommandError, "já possui uma reversão"):
            self.executar(reverter_lote=lote.identificador)

    def test_reexecucao_com_atualizar_reconcilia_campos_da_fonte(self):
        ferramentas = self.ferramentas_fonte()
        caminho, sha256 = self.criar_fonte(ferramentas)
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(titulo_es=ferramentas[0]["nombre"])
        primeira.descricao_es = "Divergência local."
        primeira.responsavel = "Responsável divergente"
        primeira.save(update_fields=("descricao_es", "responsavel", "atualizado_em"))

        self.executar(caminho, sha256, atualizar=True)

        primeira.refresh_from_db()
        self.assertEqual(primeira.descricao_es, ferramentas[0]["desc"])
        self.assertEqual(primeira.responsavel, ferramentas[0]["responsable"])
        item = LoteImportacaoConteudo.objects.order_by("iniciado_em").last().itens.get(
            entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA,
            codigo_origem=ImportarFerramentasCommand.CODIGOS_CANONICOS[ferramentas[0]["nombre"]],
        )
        self.assertEqual(item.operacao, ItemLoteImportacaoConteudo.Operacao.ATUALIZADO)
        self.assertEqual(item.snapshot_anterior["descricao_es"], "Divergência local.")

    def test_atualizacao_preserva_traducoes_pt_e_en(self):
        ferramentas = self.ferramentas_fonte()
        caminho, sha256 = self.criar_fonte(ferramentas)
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.titulo = "Título institucional"
        primeira.titulo_en = "Institutional title"
        primeira.descricao = "Descrição institucional."
        primeira.descricao_en = "Institutional description."
        primeira.descricao_es = "Divergência a reconciliar."
        primeira.save()

        self.executar(caminho, sha256, atualizar=True)

        primeira.refresh_from_db()
        self.assertEqual(primeira.titulo, "Título institucional")
        self.assertEqual(primeira.titulo_en, "Institutional title")
        self.assertEqual(primeira.descricao, "Descrição institucional.")
        self.assertEqual(primeira.descricao_en, "Institutional description.")

    def test_atualizar_nao_publica(self):
        ferramentas = self.ferramentas_fonte()
        caminho, sha256 = self.criar_fonte(ferramentas)
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.responsavel = "Responsável divergente"
        primeira.save(update_fields=("responsavel", "atualizado_em"))

        self.executar(caminho, sha256, atualizar=True)

        self.assertFalse(
            Ferramenta.objects.exclude(situacao=Ferramenta.Situacao.RASCUNHO).exists()
        )

    def test_publicar_nao_altera_traducoes(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.titulo = "Título institucional"
        primeira.titulo_en = "Institutional title"
        primeira.descricao = "Descrição institucional."
        primeira.descricao_en = "Institutional description."
        primeira.save()

        self.executar(caminho, sha256, publicar=True)

        primeira.refresh_from_db()
        self.assertEqual(primeira.situacao, Ferramenta.Situacao.PUBLICADA)
        self.assertEqual(primeira.titulo, "Título institucional")
        self.assertEqual(primeira.titulo_en, "Institutional title")
        self.assertEqual(primeira.descricao, "Descrição institucional.")
        self.assertEqual(primeira.descricao_en, "Institutional description.")

    def test_codigos_permanecem_iguais_quando_ordem_do_html_muda(self):
        ferramentas = self.ferramentas_fonte()
        caminho, sha256 = self.criar_fonte(ferramentas)
        self.executar(caminho, sha256)
        codigos_originais = dict(Ferramenta.objects.values_list("titulo_es", "codigo"))
        Ferramenta.objects.all().delete()

        caminho, sha256 = self.criar_fonte(list(reversed(ferramentas)))
        self.executar(caminho, sha256)

        self.assertEqual(
            dict(Ferramenta.objects.values_list("titulo_es", "codigo")),
            codigos_originais,
        )

    def _criar_primeira_ferramenta_legada(self):
        dados = self.ferramentas_fonte()[0]
        setor = Setor.objects.create(nome=dados["sector"], nome_es=dados["sector"])
        return Ferramenta.objects.create(
            codigo="fase2c-ferramenta-01",
            titulo="Título curado",
            titulo_en="Curated title",
            titulo_es=dados["nombre"],
            descricao="Descrição curada.",
            descricao_en="Curated description.",
            descricao_es=dados["desc"],
            responsavel=dados["responsable"],
            periodo=dados["ano"],
            setor=setor,
            url=dados["link"],
            situacao=Ferramenta.Situacao.RASCUNHO,
            ordem=1,
        )

    def test_codigo_legado_e_reconciliado_somente_com_atualizar(self):
        legada = self._criar_primeira_ferramenta_legada()
        caminho, sha256 = self.criar_fonte()

        self.executar(caminho, sha256)
        legada.refresh_from_db()
        self.assertEqual(legada.codigo, "fase2c-ferramenta-01")

        self.executar(caminho, sha256, atualizar=True)
        legada.refresh_from_db()
        self.assertEqual(
            legada.codigo,
            ImportarFerramentasCommand.CODIGOS_CANONICOS[legada.titulo_es],
        )
        self.assertEqual(legada.titulo, "Título curado")
        self.assertEqual(legada.titulo_en, "Curated title")
        self.assertEqual(legada.situacao, Ferramenta.Situacao.RASCUNHO)

    def test_reconciliacao_de_codigo_legado_nao_cria_duplicata(self):
        legada = self._criar_primeira_ferramenta_legada()
        caminho, sha256 = self.criar_fonte()

        self.executar(caminho, sha256, atualizar=True)

        legada.refresh_from_db()
        self.assertEqual(Ferramenta.objects.count(), 15)
        self.assertEqual(
            Ferramenta.objects.filter(codigo=legada.codigo).count(),
            1,
        )

    def test_rollback_remove_registros_criados_pelo_lote(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        lote = LoteImportacaoConteudo.objects.get()

        self.executar(reverter_lote=lote.identificador)

        lote.refresh_from_db()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERTIDO)
        self.assertFalse(Ferramenta.objects.exists())
        self.assertFalse(Setor.objects.exists())
        self.assertFalse(
            lote.itens.filter(
                status_rollback=ItemLoteImportacaoConteudo.StatusRollback.PENDENTE
            ).exists()
        )

    def test_rollback_restaura_registros_atualizados(self):
        ferramentas = self.ferramentas_fonte()
        caminho, sha256 = self.criar_fonte(ferramentas)
        self.executar(caminho, sha256)
        primeiro_lote = LoteImportacaoConteudo.objects.get()
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.descricao_es = "Estado anterior à reconciliação."
        primeira.save(update_fields=("descricao_es", "atualizado_em"))
        self.executar(caminho, sha256, atualizar=True)
        lote_atualizacao = LoteImportacaoConteudo.objects.order_by("iniciado_em").last()

        self.executar(reverter_lote=lote_atualizacao.identificador)

        primeira.refresh_from_db()
        self.assertEqual(primeira.descricao_es, "Estado anterior à reconciliação.")
        self.assertEqual(primeira.lote_origem_id, primeiro_lote.pk)
        lote_atualizacao.refresh_from_db()
        self.assertEqual(lote_atualizacao.status, LoteImportacaoConteudo.Status.REVERTIDO)

    def test_rollback_nao_remove_setor_reutilizado(self):
        setor = Setor.objects.create(nome="Agua y saneamiento", nome_es="Agua y saneamiento")
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        lote = LoteImportacaoConteudo.objects.get()

        self.executar(reverter_lote=lote.identificador)

        self.assertTrue(Setor.objects.filter(pk=setor.pk).exists())
        item = lote.itens.get(
            entidade=ItemLoteImportacaoConteudo.Entidade.SETOR,
            objeto_pk=str(setor.pk),
        )
        self.assertEqual(
            item.status_rollback,
            ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL,
        )

    def test_rollback_nao_remove_objeto_modificado_posteriormente(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        lote = LoteImportacaoConteudo.objects.get()
        primeira = Ferramenta.objects.get(ordem=1)
        primeira.titulo = "Curadoria posterior ao lote"
        primeira.save(update_fields=("titulo", "atualizado_em"))

        self.executar(reverter_lote=lote.identificador)

        primeira.refresh_from_db()
        lote.refresh_from_db()
        self.assertEqual(primeira.titulo, "Curadoria posterior ao lote")
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERSAO_PARCIAL)
        item = lote.itens.get(
            entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA,
            objeto_pk=str(primeira.pk),
        )
        self.assertEqual(
            item.status_rollback,
            ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
        )

    def test_combinacoes_invalidas_geram_command_error(self):
        caminho, _sha256 = self.criar_fonte()
        combinacoes = (
            {"arquivo": str(caminho)},
            {"dry_run": True},
            {"publicar": True},
            {"atualizar": True},
        )
        for adicionais in combinacoes:
            with self.subTest(adicionais=adicionais), self.assertRaises(CommandError):
                call_command(
                    "importar_ferramentas_fase2c",
                    reverter_lote="00000000-0000-0000-0000-000000000000",
                    executado_por=self.executor.username,
                    stdout=StringIO(),
                    **adicionais,
                )
        with self.assertRaisesMessage(CommandError, "exige o argumento --arquivo"):
            call_command(
                "importar_ferramentas_fase2c",
                executado_por=self.executor.username,
                stdout=StringIO(),
            )

    def test_segunda_reversao_e_recusada_sem_efeitos_duplicados(self):
        caminho, sha256 = self.criar_fonte()
        self.executar(caminho, sha256)
        lote = LoteImportacaoConteudo.objects.get()
        self.executar(reverter_lote=lote.identificador)
        estados_rollback = list(
            lote.itens.values_list("pk", "status_rollback").order_by("pk")
        )

        with self.assertRaisesMessage(CommandError, "já possui uma reversão"):
            self.executar(reverter_lote=lote.identificador)

        self.assertEqual(
            list(lote.itens.values_list("pk", "status_rollback").order_by("pk")),
            estados_rollback,
        )
        self.assertFalse(Ferramenta.objects.exists())

    def test_falha_no_atomic_reverte_conteudos_e_mantem_lote_falho(self):
        caminho, sha256 = self.criar_fonte()

        with (
            mock.patch.object(
                ImportarFerramentasCommand,
                "SHA256_FONTE_OFICIAL",
                sha256,
            ),
            mock.patch.object(
                ImportarFerramentasCommand,
                "_importar_ferramenta",
                side_effect=RuntimeError("detalhe interno não deve vazar"),
            ),
            self.assertRaises(CommandError),
        ):
            call_command(
                "importar_ferramentas_fase2c",
                arquivo=str(caminho),
                executado_por=self.executor.username,
                stdout=StringIO(),
            )

        self.assertFalse(Ferramenta.objects.exists())
        self.assertFalse(Setor.objects.exists())
        self.assertFalse(ItemLoteImportacaoConteudo.objects.exists())
        lote = LoteImportacaoConteudo.objects.get()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.FALHOU)
        self.assertTrue(lote.contagens_realizadas["rollback_aplicado"])
        self.assertNotIn("detalhe interno", lote.mensagem_sanitizada)

    def test_hash_nao_aprovado_interrompe_antes_de_criar_lote(self):
        caminho, _sha256 = self.criar_fonte()

        with self.assertRaises(CommandError):
            call_command(
                "importar_ferramentas_fase2c",
                arquivo=str(caminho),
                executado_por=self.executor.username,
                stdout=StringIO(),
            )

        self.assertFalse(LoteImportacaoConteudo.objects.exists())

    def test_quantidade_diferente_de_15_e_rejeitada(self):
        caminho, sha256 = self.criar_fonte(self.ferramentas_fonte()[:-1])

        with (
            mock.patch.object(
                ImportarFerramentasCommand,
                "SHA256_FONTE_OFICIAL",
                sha256,
            ),
            self.assertRaisesMessage(CommandError, "exatamente 15 ferramentas"),
        ):
            call_command(
                "importar_ferramentas_fase2c",
                arquivo=str(caminho),
                executado_por=self.executor.username,
                dry_run=True,
                stdout=StringIO(),
            )
