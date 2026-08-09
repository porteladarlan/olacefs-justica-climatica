import copy
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from .management.commands.validar_fonte_guia_fase2d2 import (
    ErroFonteGuia,
    _calcular_sha256_guia_canonico,
    validar_documento,
)
from .models import (
    EixoGuia,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    PerguntaGuia,
    ReferenciaGuia,
    Setor,
    SetorGuia,
    SubareaGuia,
    SubareaReferenciaGuia,
    SubeixoGuia,
    VersaoGuia,
)
from .servicos_guia_fase2d2 import DivergenciaGuia, importar, planejar_importacao


def fonte_sintetica(codigo="guia-sintetico-v1"):
    guia = {
        "eixos": [{
            "codigo": "eixo-1", "nome_es": "Eje uno", "ordem": 1,
            "perguntas": [{"codigo": "p-eixo", "texto_es": "¿Eje?", "tipo_auditoria": "cumplimiento", "ordem": 1}],
            "subeixos": [{
                "codigo": "subeixo-1", "nome_es": "Subeje uno", "ordem": 1,
                "perguntas": [{"codigo": "p-subeixo", "texto_es": "¿Subeje?", "tipo_auditoria": "gestion", "ordem": 1}],
            }],
        }],
        "setores": [{
            "codigo": "setor-1", "nome_es": "Sector uno", "ordem": 1,
            "subareas": [{
                "codigo": "subarea-1", "nome_es": "Subárea uno", "ordem": 1,
                "perguntas": [{"codigo": "p-subarea", "texto_es": "¿Subárea?", "tipo_auditoria": "cumplimiento", "ordem": 1}],
                "referencias": [
                    {"codigo_referencia": "ref-compartida", "ordem": 1},
                    {"codigo_referencia": "ref-unica", "ordem": 2},
                ],
            }, {
                "codigo": "subarea-2", "nome_es": "Subárea dos", "ordem": 2,
                "perguntas": [],
                "referencias": [{"codigo_referencia": "ref-compartida", "ordem": 1}],
            }],
        }],
        "referencias": [
            {"codigo": "ref-compartida", "citacao_es": "Referencia compartida"},
            {"codigo": "ref-unica", "citacao_es": "Referencia única"},
        ],
    }
    contagens = {"eixos": 1, "subeixos": 1, "setores": 1, "subareas": 2, "perguntas": 3, "ocorrencias_referencias": 3, "referencias": 2}
    sha = hashlib.sha256(json.dumps(guia, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    documento = {
        "contrato": "guia-fase2d2-v1",
        "idioma_canonico": "es",
        "versao": {"codigo": codigo, "fonte": "institucional/sintetica.json", "sha256_fonte": "a" * 64},
        "guia": guia, "sha256_guia": sha, "contagens": contagens,
    }
    with (
        patch(
            "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
            _calcular_sha256_guia_canonico(guia),
        ),
        patch(
            "praticas.management.commands.validar_fonte_guia_fase2d2.CONTAGENS_OFICIAIS",
            contagens,
        ),
        patch(
            "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
            "a" * 64,
        ),
    ):
        resultado = validar_documento(documento)
    return documento, resultado


class ValidacaoFonteGuiaFase2D2Tests(TestCase):
    def test_fixture_valida_e_preserva_canonicalizacao_sem_sort_keys(self):
        documento, resultado = fonte_sintetica()
        self.assertEqual(resultado["sha256_guia"], documento["sha256_guia"])
        self.assertEqual(resultado["contagens"]["perguntas"], 3)

    def test_rejeita_hash_canonico_declarado_divergente(self):
        documento, _ = fonte_sintetica()
        documento["sha256_guia"] = "0" * 64
        with self.assertRaisesRegex(ErroFonteGuia, "Hash canonico"):
            with patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                "a" * 64,
            ):
                validar_documento(documento)

    def test_rejeita_contrato_hash_contagens_codigo_tipo_e_referencia_invalidos(self):
        for mutacao, trecho in (
            (lambda d: d.update(contrato="outro"), "Contrato invalido"),
            (lambda d: d["contagens"].update(perguntas=99), "Contagens"),
            (lambda d: d["guia"]["eixos"][0].update(codigo="com espaco"), "codigo institucional"),
            (lambda d: d["guia"]["eixos"][0]["perguntas"][0].update(tipo_auditoria="outro"), "tipo_auditoria"),
            (lambda d: d["guia"]["setores"][0]["subareas"][0]["referencias"][0].update(codigo_referencia="ausente"), "codigo inexistente"),
        ):
            documento, _ = fonte_sintetica()
            mutacao(documento)
            guia_hash = hashlib.sha256(json.dumps(documento["guia"], ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            documento["sha256_guia"] = guia_hash
            with self.assertRaisesRegex(ErroFonteGuia, trecho):
                with (
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
                        "0" * 64,
                    ),
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.CONTAGENS_OFICIAIS",
                        fonte_sintetica()[0]["contagens"],
                    ),
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                        "a" * 64,
                    ),
                ):
                    validar_documento(documento)


class ImportacaoGuiaFase2D2Tests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user("staff-guia", is_staff=True)
        self.resultado = fonte_sintetica()[1]

    def test_dry_run_command_nao_escreve(self):
        with patch("praticas.management.commands.importar_guia_fase2d2.ler_e_validar", return_value=self.resultado):
            call_command("importar_guia_fase2d2", arquivo="ignorado.json", executado_por=self.staff.username, dry_run=True)
        self.assertFalse(VersaoGuia.objects.exists())
        self.assertFalse(LoteImportacaoConteudo.objects.exists())
        self.assertFalse(ItemLoteImportacaoConteudo.objects.exists())

    def test_autorizacao_rejeita_executor_inexistente_inativo_e_nao_staff(self):
        inativo = get_user_model().objects.create_user("inativo", is_staff=True, is_active=False)
        comum = get_user_model().objects.create_user("comum")
        for username, trecho in (("ausente", "inexistente"), (inativo.username, "ativo"), (comum.username, "staff")):
            with self.assertRaisesRegex(CommandError, trecho):
                call_command("importar_guia_fase2d2", arquivo="qualquer", executado_por=username, dry_run=True)

    def test_importacao_cria_rascunho_hierarquia_conteudo_e_ledger(self):
        lote, plano = importar(self.resultado, self.staff)
        versao = VersaoGuia.objects.get(codigo="guia-sintetico-v1")
        self.assertTrue(plano.criar_versao)
        self.assertEqual((versao.situacao, versao.vigente, versao.publicado_em), ("rascunho", False, None))
        self.assertEqual((versao.eixos.count(), versao.subeixos.count(), versao.setores.count(), versao.subareas.count(), versao.perguntas.count(), versao.referencias.count()), (1, 1, 1, 2, 3, 2))
        self.assertEqual(SubareaReferenciaGuia.objects.count(), 3)
        self.assertEqual(ReferenciaGuia.objects.get(codigo="ref-compartida").ocorrencias_subareas.count(), 2)
        self.assertEqual(PerguntaGuia.objects.get(codigo="p-eixo").eixo.codigo, "eixo-1")
        self.assertEqual(PerguntaGuia.objects.get(codigo="p-subeixo").subeixo.codigo, "subeixo-1")
        self.assertEqual(PerguntaGuia.objects.get(codigo="p-subarea").subarea.codigo, "subarea-1")
        self.assertTrue(all(sum(bool(getattr(p, f"{e}_id")) for e in ("eixo", "subeixo", "subarea")) == 1 for p in versao.perguntas.all()))
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.CONCLUIDO)
        self.assertEqual(lote.itens.count(), 1 + 1 + 1 + 1 + 2 + 3 + 2 + 3)
        self.assertEqual(lote.itens.filter(operacao="criado", status_rollback="pendente").count(), lote.itens.count())
        self.assertFalse(Setor.objects.exists())

    def test_reexecucao_identica_nao_duplica_e_registra_ignorados(self):
        importar(self.resultado, self.staff)
        lote, plano = importar(self.resultado, self.staff)
        self.assertFalse(plano.criar_versao)
        self.assertEqual(plano.novos, 0)
        self.assertEqual(lote.itens.exclude(operacao="ignorado").count(), 0)
        self.assertEqual(VersaoGuia.objects.count(), 1)
        self.assertEqual(PerguntaGuia.objects.count(), 3)

    def test_divergencia_explicita_bloqueia_sem_novo_lote(self):
        importar(self.resultado, self.staff)
        PerguntaGuia.objects.filter(codigo="p-eixo").update(texto_es="Alteración local")
        antes = LoteImportacaoConteudo.objects.count()
        plano = planejar_importacao(self.resultado)
        self.assertIn({"entidade": "pergunta", "codigo": "p-eixo", "campo": "texto_es"}, plano.divergencias)
        with self.assertRaisesRegex(DivergenciaGuia, "pergunta p-eixo, campo texto_es"):
            importar(self.resultado, self.staff)
        self.assertEqual(LoteImportacaoConteudo.objects.count(), antes)

    def test_divergencia_criada_depois_do_planejamento_nao_vira_ignorado(self):
        importar(self.resultado, self.staff)
        lotes_antes = LoteImportacaoConteudo.objects.count()
        itens_antes = ItemLoteImportacaoConteudo.objects.count()
        criar_lote = LoteImportacaoConteudo.objects.create

        def criar_lote_e_divergir(*args, **kwargs):
            lote = criar_lote(*args, **kwargs)
            PerguntaGuia.objects.filter(codigo="p-eixo").update(
                texto_es="Divergencia concorrente"
            )
            return lote

        with patch.object(
            LoteImportacaoConteudo.objects,
            "create",
            side_effect=criar_lote_e_divergir,
        ):
            with self.assertRaisesRegex(
                DivergenciaGuia,
                "Divergencia concorrente em pergunta p-eixo, campo texto_es",
            ):
                importar(self.resultado, self.staff)

        self.assertEqual(LoteImportacaoConteudo.objects.count(), lotes_antes)
        self.assertEqual(ItemLoteImportacaoConteudo.objects.count(), itens_antes)
        self.assertEqual(
            PerguntaGuia.objects.get(codigo="p-eixo").texto_es,
            self.resultado["guia"]["eixos"][0]["perguntas"][0]["texto_es"],
        )

    def test_conflito_ao_criar_versao_com_fonte_divergente_reverte_lote(self):
        criar_lote = LoteImportacaoConteudo.objects.create

        def criar_lote_e_versao_concorrente(*args, **kwargs):
            lote = criar_lote(*args, **kwargs)
            VersaoGuia.objects.create(
                codigo=self.resultado["versao"]["codigo"],
                fonte="concorrente/divergente.json",
                sha256_fonte=self.resultado["versao"]["sha256_fonte"],
                lote_origem=lote,
            )
            return lote

        with patch.object(
            LoteImportacaoConteudo.objects,
            "create",
            side_effect=criar_lote_e_versao_concorrente,
        ):
            with self.assertRaisesRegex(
                DivergenciaGuia,
                "Divergencia concorrente em versao_guia.*campo fonte",
            ):
                importar(self.resultado, self.staff)

        self.assertFalse(LoteImportacaoConteudo.objects.exists())
        self.assertFalse(VersaoGuia.objects.exists())
        self.assertFalse(ItemLoteImportacaoConteudo.objects.exists())

    def test_nova_versao_preserva_anterior(self):
        importar(self.resultado, self.staff)
        _, outro = fonte_sintetica("guia-sintetico-v2")
        importar(outro, self.staff)
        self.assertEqual(VersaoGuia.objects.count(), 2)
        self.assertEqual(PerguntaGuia.objects.count(), 6)

    def test_falha_no_meio_da_importacao_e_atomica(self):
        with patch("praticas.servicos_guia_fase2d2._item", side_effect=RuntimeError("falha sintética")):
            with self.assertRaises(RuntimeError):
                importar(self.resultado, self.staff)
        self.assertFalse(VersaoGuia.objects.exists())
        self.assertFalse(LoteImportacaoConteudo.objects.exists())

class PublicacaoReversaoGuiaFase2D2Tests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user("publicador", is_staff=True)
        self.resultado = fonte_sintetica()[1]

    def test_publicacao_e_separada_atomica_e_troca_unica_vigente(self):
        lote1, _ = importar(self.resultado, self.staff)
        call_command("publicar_guia_fase2d2", versao="guia-sintetico-v1", executado_por=self.staff.username, vigente=True)
        primeira = VersaoGuia.objects.get(codigo="guia-sintetico-v1")
        self.assertEqual(primeira.situacao, VersaoGuia.Situacao.PUBLICADA)
        self.assertTrue(primeira.vigente)
        self.assertIsNotNone(primeira.publicado_em)
        _, resultado2 = fonte_sintetica("guia-sintetico-v2")
        importar(resultado2, self.staff)
        call_command("publicar_guia_fase2d2", versao="guia-sintetico-v2", executado_por=self.staff.username, vigente=True)
        primeira.refresh_from_db()
        self.assertFalse(primeira.vigente)
        self.assertEqual(VersaoGuia.objects.filter(vigente=True).count(), 1)
        self.assertEqual(lote1.status, LoteImportacaoConteudo.Status.CONCLUIDO)

    def test_publicacao_rejeita_nao_staff_versao_ausente_e_rascunho_sem_lote(self):
        comum = get_user_model().objects.create_user("nao-publicador")
        with self.assertRaisesRegex(CommandError, "staff"):
            call_command("publicar_guia_fase2d2", versao="x", executado_por=comum.username)
        with self.assertRaisesRegex(CommandError, "inexistente"):
            call_command("publicar_guia_fase2d2", versao="x", executado_por=self.staff.username)
        VersaoGuia.objects.create(codigo="manual", fonte="manual", sha256_fonte="b" * 64)
        with self.assertRaisesRegex(CommandError, "proveniencia"):
            call_command("publicar_guia_fase2d2", versao="manual", executado_por=self.staff.username)

    def test_publicacao_rejeita_conteudo_editado_depois_da_importacao(self):
        importar(self.resultado, self.staff)
        pergunta = PerguntaGuia.objects.get(codigo="p-eixo")
        pergunta.texto_es = "Edicion posterior aun no homologada"
        pergunta.save()

        with self.assertRaisesRegex(CommandError, "Integridade.*pergunta p-eixo"):
            call_command(
                "publicar_guia_fase2d2",
                versao="guia-sintetico-v1",
                executado_por=self.staff.username,
            )

        self.assertEqual(
            VersaoGuia.objects.get(codigo="guia-sintetico-v1").situacao,
            VersaoGuia.Situacao.RASCUNHO,
        )

    def test_save_e_delete_releem_versao_publicada_apesar_de_cache_rascunho(self):
        importar(self.resultado, self.staff)
        pergunta = PerguntaGuia.objects.select_related("versao").get(
            codigo="p-eixo"
        )
        self.assertEqual(
            pergunta.versao.situacao,
            VersaoGuia.Situacao.RASCUNHO,
        )
        VersaoGuia.objects.filter(pk=pergunta.versao_id).update(
            situacao=VersaoGuia.Situacao.PUBLICADA,
            publicado_em=timezone.now(),
        )

        pergunta.texto_es = "Edicion iniciada durante la publicacion"
        with self.assertRaisesRegex(ValidationError, "publicada e imutavel"):
            pergunta.save()
        with self.assertRaisesRegex(ValidationError, "publicada e imutavel"):
            pergunta.delete()

        pergunta.refresh_from_db()
        self.assertEqual(
            pergunta.texto_es,
            self.resultado["guia"]["eixos"][0]["perguntas"][0]["texto_es"],
        )

    def test_versao_publicada_bloqueia_divergencia_e_reversao_destrutiva(self):
        lote, _ = importar(self.resultado, self.staff)
        call_command("publicar_guia_fase2d2", versao="guia-sintetico-v1", executado_por=self.staff.username)
        alterado = copy.deepcopy(self.resultado)
        alterado["guia"]["eixos"][0]["nome_es"] = "Otro nombre"
        with self.assertRaises(DivergenciaGuia):
            importar(alterado, self.staff)
        call_command("importar_guia_fase2d2", reverter_lote=str(lote.identificador), executado_por=self.staff.username, justificativa="Teste de proteção")
        lote.refresh_from_db()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERSAO_PARCIAL)
        self.assertTrue(VersaoGuia.objects.filter(pk=lote.versoes_guia.get().pk).exists())
        self.assertTrue(lote.itens.filter(status_rollback="bloqueado").exists())

    def test_reversao_remove_criados_quando_estado_nao_mudou(self):
        lote, _ = importar(self.resultado, self.staff)
        call_command("importar_guia_fase2d2", reverter_lote=str(lote.identificador), executado_por=self.staff.username, justificativa="Carga sintética equivocada")
        lote.refresh_from_db()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERTIDO)
        self.assertFalse(VersaoGuia.objects.exists())
        self.assertFalse(EixoGuia.objects.exists())
        self.assertEqual(lote.itens.filter(status_rollback="revertido").count(), lote.itens.count())

    def test_reversao_bloqueia_item_alterado_posteriormente_sem_sobrescrever(self):
        lote, _ = importar(self.resultado, self.staff)
        pergunta = PerguntaGuia.objects.get(codigo="p-eixo")
        pergunta.texto_es = "Edición local posterior"
        pergunta.save()
        call_command("importar_guia_fase2d2", reverter_lote=str(lote.identificador), executado_por=self.staff.username, justificativa="Teste parcial")
        lote.refresh_from_db()
        pergunta.refresh_from_db()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERSAO_PARCIAL)
        self.assertEqual(pergunta.texto_es, "Edición local posterior")
        self.assertEqual(lote.itens.get(entidade="pergunta", codigo_origem="p-eixo").status_rollback, "bloqueado")

    def test_reversao_bloqueia_alteracao_por_queryset_update(self):
        lote, _ = importar(self.resultado, self.staff)
        pergunta = PerguntaGuia.objects.get(codigo="p-eixo")
        atualizado_em_original = pergunta.atualizado_em
        PerguntaGuia.objects.filter(pk=pergunta.pk).update(
            texto_es="Edición posterior sin actualizar timestamp"
        )

        pergunta.refresh_from_db()
        self.assertEqual(pergunta.atualizado_em, atualizado_em_original)
        call_command(
            "importar_guia_fase2d2",
            reverter_lote=str(lote.identificador),
            executado_por=self.staff.username,
            justificativa="Teste de snapshot completo",
        )

        lote.refresh_from_db()
        pergunta.refresh_from_db()
        self.assertEqual(lote.status, LoteImportacaoConteudo.Status.REVERSAO_PARCIAL)
        self.assertEqual(
            pergunta.texto_es,
            "Edición posterior sin actualizar timestamp",
        )
        self.assertEqual(
            lote.itens.get(
                entidade="pergunta", codigo_origem="p-eixo"
            ).status_rollback,
            "bloqueado",
        )
