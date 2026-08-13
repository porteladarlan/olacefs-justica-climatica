import json
from copy import deepcopy
from html import unescape
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .management.commands.importar_marcos_normativos_lote2 import Command
from .models import (
    EFS,
    Experiencia,
    NormaInternacional,
    NormaInternacionalPais,
    Pais,
    Setor,
    TipoExperiencia,
)


class MarcosNormativosLote2Tests(TestCase):
    def setUp(self):
        self.client.cookies.clear()
        translation.activate("pt-br")

    def tearDown(self):
        self.client.cookies.clear()
        translation.deactivate_all()

    def _card_renderizado(self, response, norma):
        html = response.content.decode("utf-8")
        inicio = html.index(f'id="norma-card-{norma.pk}"')
        return html[inicio : html.index("</article>", inicio)]

    def _dialog_renderizado(self, response, norma):
        html = response.content.decode("utf-8")
        inicio = html.index(f'id="norma-{norma.pk}"')
        return html[inicio : html.index("</dialog>", inicio)]

    @classmethod
    def setUpTestData(cls):
        cls.brasil = Pais.objects.create(
            nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA"
        )
        cls.chile = Pais.objects.create(
            nome="Chile", nome_es="Chile", nome_en="Chile", sigla="CHL"
        )
        cls.efs = EFS.objects.create(nome="EFS", pais=cls.brasil)
        cls.setor = Setor.objects.create(nome="Energia")
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria")
        cls.vinculante = NormaInternacional.objects.create(
            nome="Marco vinculante",
            nome_es="Marco vinculante",
            ano=2018,
            ano_texto="2018",
            natureza_juridica="Vinculante",
            setores_aplicaveis="Agua y Energía, Infraestructura",
            cobertura_paises_es="Cobertura institucional do marco.",
            resumo_es="Introducción institucional aprobada.",
            url_referencia="https://example.org/fonte-oficial",
            ficha_tecnica_url="https://example.org/ficha-tecnica",
        )
        cls.nao_vinculante = NormaInternacional.objects.create(
            nome="Marco não vinculante",
            nome_es="Marco no vinculante",
            natureza_juridica="No vinculante",
            setores_aplicaveis="Salud",
            cobertura_paises_es="Aplicable a los miembros de OLACEFS.",
            resumo_es="Otra introducción institucional.",
        )
        NormaInternacionalPais.objects.create(
            norma=cls.vinculante,
            pais=cls.brasil,
            status="Firmado (2018), no ratificado",
        )
        experiencia = Experiencia.objects.create(
            titulo="Prática pública",
            efs=cls.efs,
            pais=cls.chile,
            tipo_experiencia=cls.tipo,
            setor=cls.setor,
            ano_execucao=2025,
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        experiencia.normas_internacionais.add(cls.vinculante)

    def test_filtro_de_natureza_juridica_e_dinamico_e_funcional(self):
        response = self.client.get(
            reverse("normas_internacionais"),
            {"natureza": "Vinculante"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 1)
        self.assertContains(response, 'name="natureza"')
        self.assertContains(response, 'value="Vinculante" selected')
        self.assertContains(response, self.vinculante.nome)
        self.assertNotContains(response, self.nao_vinculante.nome)

    def test_paises_e_status_sao_do_marco_e_nao_das_praticas(self):
        response = self.client.get(reverse("normas_internacionais"))
        card = unescape(self._card_renderizado(response, self.vinculante))

        self.assertIn("Brasil: <span lang=\"es\">Firmado (2018), no ratificado</span>", card)
        self.assertNotContains(response, "Países vinculados a práticas públicas")
        self.assertNotContains(response, "Countries linked to public practices")
        self.assertNotIn("Chile:", card)
        self.assertContains(response, "Aplicable a los miembros de OLACEFS")

        filtrado_por_cobertura_textual = self.client.get(
            reverse("normas_internacionais"), {"pais": self.chile.pk}
        )
        self.assertEqual(filtrado_por_cobertura_textual.context["total_resultados"], 0)

    def test_card_limita_paises_e_status_a_tres_e_indica_continuacao(self):
        vinculos = (
            ("Argentina", "ARG", "Adhesión registrada"),
            ("Colômbia", "COL", "Ratificación pendiente"),
            ("Peru", "PER", "Parte desde 2020"),
        )
        for nome, sigla, status in vinculos:
            pais = Pais.objects.create(nome=nome, nome_es=nome, sigla=sigla)
            NormaInternacionalPais.objects.create(
                norma=self.vinculante,
                pais=pais,
                status=status,
            )

        response = self.client.get(reverse("normas_internacionais"))
        card = unescape(self._card_renderizado(response, self.vinculante))

        self.assertIn('Argentina: <span lang="es">Adhesión registrada</span>', card)
        self.assertIn(
            'Brasil: <span lang="es">Firmado (2018), no ratificado</span>',
            card,
        )
        self.assertIn(
            'Colômbia: <span lang="es">Ratificación pendiente</span>',
            card,
        )
        self.assertNotIn("Peru: <span", card)
        self.assertIn("…", card)

    def test_descricao_fontes_e_saiba_mais_sao_campos_separados(self):
        response = self.client.get(reverse("normas_internacionais"))
        card = self._card_renderizado(response, self.vinculante)
        dialogo = self._dialog_renderizado(response, self.vinculante)

        self.assertContains(response, 'lang="es">Introducción institucional aprobada.')
        for trecho in (
            'href="https://example.org/fonte-oficial"',
            'href="https://example.org/ficha-tecnica"',
            "Fonte oficial",
            "Saiba mais",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, card)
                self.assertIn(trecho, dialogo)
        self.assertIn("Pr&aacute;ticas relacionadas", dialogo)

    def test_urls_invalidas_nao_sao_publicadas(self):
        self.vinculante.url_referencia = (
            "[https://example.org/fonte](https://example.org/fonte)"
        )
        self.vinculante.ficha_tecnica_url = "javascript:alert(2)"
        self.vinculante.save(update_fields=["url_referencia", "ficha_tecnica_url"])

        response = self.client.get(reverse("normas_internacionais"))

        self.assertNotContains(response, "javascript:")
        self.assertNotContains(response, "Fonte oficial")
        self.assertNotContains(response, "Saiba mais")
        self.assertNotContains(response, "[https://")

    def test_botoes_de_fonte_e_ficha_ausentes_quando_urls_estao_vazias(self):
        response = self.client.get(reverse("normas_internacionais"))
        card = self._card_renderizado(response, self.nao_vinculante)
        dialogo = self._dialog_renderizado(response, self.nao_vinculante)

        for trecho in ("Fonte oficial", "Saiba mais", 'href=""'):
            with self.subTest(trecho=trecho):
                self.assertNotIn(trecho, card)
                self.assertNotIn(trecho, dialogo)

    def test_saiba_mais_ausente_quando_arquivo_media_nao_existe(self):
        self.nao_vinculante.ficha_tecnica.name = (
            "marcos_normativos/fichas/arquivo-ainda-nao-publicado.pdf"
        )
        self.nao_vinculante.save(update_fields=["ficha_tecnica"])

        response = self.client.get(reverse("normas_internacionais"))

        self.assertNotIn(
            "Saiba mais",
            self._card_renderizado(response, self.nao_vinculante),
        )
        self.assertNotIn(
            "Saiba mais",
            self._dialog_renderizado(response, self.nao_vinculante),
        )

    def test_rotulos_sao_trilingues(self):
        casos = (
            ("/normas-internacionais/", "Natureza jurídica", "Fonte oficial", "Saiba mais"),
            ("/es/normas-internacionais/", "Naturaleza jurídica", "Fuente oficial", "Saber más"),
            ("/en/normas-internacionais/", "Legal nature", "Official source", "Learn more"),
        )
        for caminho, natureza, fonte, ficha in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode("utf-8")
                self.assertIn(natureza, html.replace("&iacute;", "í"))
                card = unescape(self._card_renderizado(response, self.vinculante))
                dialogo = unescape(self._dialog_renderizado(response, self.vinculante))
                self.assertIn(fonte, card)
                self.assertIn(fonte, dialogo)
                self.assertIn(ficha, card)
                self.assertIn(ficha, dialogo)

    def test_compendio_sem_pdf_final_permanece_indisponivel(self):
        response = self.client.get(reverse("normas_internacionais"))

        self.assertContains(
            response,
            "Comp&ecirc;ndio institucional em prepara&ccedil;&atilde;o",
            html=False,
        )
        self.assertContains(response, "library-compendium", html=False)
        self.assertContains(response, "disabled")
        self.assertNotContains(response, "download=")

    def test_fonte_versionada_nao_depende_de_local(self):
        fonte = Path(__file__).resolve().parent / "data" / "marcos_normativos_lote2.json"
        conteudo = fonte.read_text(encoding="utf-8")

        self.assertNotIn(".local", conteudo)
        self.assertNotIn(".docx", conteudo)
        self.assertNotIn("file://", conteudo.lower())
        self.assertNotIn("C:\\Users\\", conteudo)
        dados = json.loads(conteudo)
        self.assertEqual(dados["quantidade"], 34)

        urls = [marco["fonte_oficial_url"] for marco in dados["marcos"]]
        self.assertEqual(sum(bool(url) for url in urls), 27)
        self.assertEqual(sum(not url for url in urls), 7)
        for marco in dados["marcos"]:
            for campo in ("fonte_oficial_url", "ficha_tecnica_url"):
                url = marco[campo]
                self.assertNotRegex(url, r"\[[^\]]+\]\([^)]+\)")
                if url:
                    self.assertTrue(url.startswith(("http://", "https://")))

    def test_runtime_do_lote2_nao_aponta_para_local(self):
        raiz = Path(__file__).resolve().parent.parent
        caminhos = (
            raiz / "praticas" / "management" / "commands" / "importar_marcos_normativos_lote2.py",
            raiz / "praticas" / "views.py",
            raiz / "templates" / "praticas" / "normas_internacionais.html",
        )
        for caminho in caminhos:
            with self.subTest(caminho=caminho.name):
                self.assertNotIn(".local", caminho.read_text(encoding="utf-8"))


class ImportacaoMarcosNormativosLote2Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fonte = Path(__file__).resolve().parent / "data" / "marcos_normativos_lote2.json"
        dados = json.loads(fonte.read_text(encoding="utf-8"))
        nomes = sorted(
            {
                vinculo["pais"]
                for marco in dados["marcos"]
                for vinculo in marco["paises_status"]
            }
        )
        for indice, nome in enumerate(nomes, start=1):
            Pais.objects.create(
                nome=nome,
                nome_es=nome,
                sigla=f"P{indice:02d}"[-3:],
            )

        NormaInternacional.objects.create(nome="Acordo de Paris")
        NormaInternacional.objects.create(nome="Acordo de Escazú")
        NormaInternacional.objects.create(nome="Agenda 2030 — ODS 13")
        NormaInternacional.objects.create(
            nome="Marco de Sendai para Redução do Risco de Desastres"
        )
        NormaInternacional.objects.create(nome="ISSAI 140 — Gestão da qualidade")

    def test_carga_e_idempotente_reconcilia_quatro_e_preserva_conflito(self):
        saida = StringIO()
        call_command("importar_marcos_normativos_lote2", stdout=saida)
        ids = dict(NormaInternacional.objects.values_list("nome", "pk"))
        total_primeira = NormaInternacional.objects.count()
        vinculos_primeira = NormaInternacionalPais.objects.count()

        call_command("importar_marcos_normativos_lote2", stdout=StringIO())

        self.assertEqual(total_primeira, 35)
        self.assertEqual(NormaInternacional.objects.count(), 35)
        self.assertEqual(vinculos_primeira, 253)
        self.assertEqual(NormaInternacionalPais.objects.count(), 253)
        self.assertEqual(
            ids["Acordo de Paris"],
            NormaInternacional.objects.get(nome="Acordo de Paris").pk,
        )
        self.assertTrue(
            NormaInternacional.objects.filter(
                nome="ISSAI 140 — Gestão da qualidade"
            ).exists()
        )
        self.assertIn("30 criados, 4 atualizados", saida.getvalue())

    def _dados(self):
        fonte = Path(__file__).resolve().parent / "data" / "marcos_normativos_lote2.json"
        return json.loads(fonte.read_text(encoding="utf-8"))["marcos"]

    def test_validacao_aceita_urls_http_https_puras(self):
        marcos = self._dados()
        marcos[0]["fonte_oficial_url"] = "http://example.org/fonte"
        marcos[0]["ficha_tecnica_url"] = "https://example.org/ficha"

        Command()._validar(marcos)

    def test_validacao_permite_fonte_e_ficha_vazias(self):
        marcos = self._dados()
        marcos[0]["fonte_oficial_url"] = ""
        marcos[0]["ficha_tecnica_url"] = ""

        Command()._validar(marcos)

    def test_validacao_rejeita_url_markdown(self):
        for campo in ("fonte_oficial_url", "ficha_tecnica_url"):
            with self.subTest(campo=campo):
                marcos = deepcopy(self._dados())
                marcos[0][campo] = "[https://example.org](https://example.org)"
                with self.assertRaises(CommandError):
                    Command()._validar(marcos)

    def test_validacao_rejeita_texto_livre_e_esquema_nao_http(self):
        for valor in ("ONU — referência oficial", "ftp://example.org/fonte"):
            with self.subTest(valor=valor):
                marcos = deepcopy(self._dados())
                marcos[0]["fonte_oficial_url"] = valor
                with self.assertRaises(CommandError):
                    Command()._validar(marcos)
