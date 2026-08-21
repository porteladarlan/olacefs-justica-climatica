import html
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import (
    BancoTecnico,
    EFS,
    Experiencia,
    NormaInternacional,
    Pais,
    Setor,
    TipoExperiencia,
)


class FidelidadeCatalogosPublicosTests(TestCase):
    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    @classmethod
    def setUpTestData(cls):
        cls.autor = get_user_model().objects.create_user(
            username="autor-catalogos",
            password="SenhaForte123!",
        )
        cls.pais_a = Pais.objects.create(
            nome="País A",
            nome_es="País A",
            nome_en="Country A",
            sigla="PAA",
        )
        cls.pais_b = Pais.objects.create(
            nome="País B",
            nome_es="País B",
            nome_en="Country B",
            sigla="PBB",
        )
        cls.efs_a = EFS.objects.create(
            nome="EFS A",
            nome_es="EFS A",
            nome_en="SAI A",
            sigla="EFSA",
            pais=cls.pais_a,
        )
        cls.efs_b = EFS.objects.create(
            nome="EFS B",
            nome_es="EFS B",
            nome_en="SAI B",
            sigla="EFSB",
            pais=cls.pais_b,
        )
        cls.tipo = TipoExperiencia.objects.create(
            nome="Auditoria",
            nome_es="Auditoría",
            nome_en="Audit",
        )
        cls.setor_a = Setor.objects.create(
            nome="Água",
            nome_es="Agua",
            nome_en="Water",
        )
        cls.setor_b = Setor.objects.create(
            nome="Energia",
            nome_es="Energía",
            nome_en="Energy",
        )
        cls.publica_a = cls._criar_experiencia(
            "Prática pública A",
            "Práctica pública A",
            "Public practice A",
            cls.efs_a,
            cls.pais_a,
            cls.setor_a,
            2026,
            Experiencia.StatusPublicacao.PUBLICADO,
        )
        cls.publica_b = cls._criar_experiencia(
            "Prática pública B",
            "Práctica pública B",
            "Public practice B",
            cls.efs_b,
            cls.pais_b,
            cls.setor_b,
            2025,
            Experiencia.StatusPublicacao.PUBLICADO,
        )
        cls.publica_b.ferramentas_utilizadas = "Painel de indicadores"
        cls.publica_b.ferramentas_utilizadas_es = "Panel de indicadores"
        cls.publica_b.ferramentas_utilizadas_en = "Indicator dashboard"
        cls.publica_b.save(
            update_fields=[
                "ferramentas_utilizadas",
                "ferramentas_utilizadas_es",
                "ferramentas_utilizadas_en",
            ]
        )
        cls.rascunho = cls._criar_experiencia(
            "Rascunho secreto",
            "Borrador secreto",
            "Secret draft",
            cls.efs_a,
            cls.pais_a,
            cls.setor_a,
            2099,
            Experiencia.StatusPublicacao.RASCUNHO,
        )
        cls.norma = NormaInternacional.objects.create(
            nome="Marco climático verificável",
            nome_es="Marco climático verificable",
            nome_en="Verifiable climate framework",
            resumo="Resumo oficial do marco.",
            resumo_es="Resumen oficial del marco.",
            resumo_en="Official framework summary.",
            url_referencia="https://example.org/framework",
        )
        cls.publica_a.normas_internacionais.add(cls.norma)
        cls.norma_b = NormaInternacional.objects.create(
            nome="Segundo marco verificável",
            nome_es="Segundo marco verificable",
            nome_en="Second verifiable framework",
            resumo="Segundo resumo oficial.",
            resumo_es="Segundo resumen oficial.",
            resumo_en="Second official summary.",
        )
        cls.publica_b.normas_internacionais.add(cls.norma_b)
        BancoTecnico.objects.create(
            titulo="Roteiro demonstrativo que não deve ser publicado",
            titulo_es="Guía demostrativa que no debe publicarse",
            titulo_en="Demonstration guide that must not be published",
            descricao="Registro sem situação editorial.",
            tipo_recurso="Roteiro metodológico",
            setor=cls.setor_a,
        )

    @classmethod
    def _criar_experiencia(
        cls, titulo, titulo_es, titulo_en, efs, pais, setor, ano, status
    ):
        return Experiencia.objects.create(
            autor=cls.autor,
            titulo=titulo,
            titulo_es=titulo_es,
            titulo_en=titulo_en,
            efs=efs,
            pais=pais,
            tipo_experiencia=cls.tipo,
            setor=setor,
            ano_execucao=ano,
            descricao="Descrição pública de teste.",
            descricao_es="Descripción pública de prueba.",
            descricao_en="Public test description.",
            ferramentas_utilizadas="Matriz de critérios",
            ferramentas_utilizadas_es="Matriz de criterios",
            ferramentas_utilizadas_en="Criteria matrix",
            status_publicacao=status,
        )

    def test_catalogo_trilingue_usa_sidebar_e_somente_publicados(self):
        casos = (
            ("/catalogo/", "Boas pr&aacute;ticas em justi&ccedil;a clim&aacute;tica"),
            ("/es/catalogo/", "Buenas pr&aacute;cticas en justicia clim&aacute;tica"),
            ("/en/catalogo/", "Good practices in climate justice"),
        )
        for caminho, titulo in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, 'class="catalog-layout"')
                self.assertContains(response, "data-filter-search", count=4)
                self.assertContains(response, 'class="catalog-filter-label"', count=4)
                self.assertNotContains(response, 'for="catalog-search"')
                self.assertContains(response, 'role="status"')
                self.assertContains(response, self.publica_a.titulo_exibicao)
                self.assertContains(response, self.publica_b.titulo_exibicao)
                self.assertNotContains(response, self.rascunho.titulo)
                self.assertNotContains(response, "2099")
                for icon_name in ("account_circle", "contrast", "balance", "download", "search"):
                    self.assertNotContains(response, f">{icon_name}<")

    def test_catalogo_remove_filtro_publico_de_fontes_de_informacao(self):
        for caminho in ("/catalogo/", "/es/catalogo/", "/en/catalogo/"):
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                conteudo = html.unescape(response.content.decode("utf-8"))
                self.assertNotIn("FONTES DE INFORMAÇÃO OU EVIDÊNCIAS", conteudo)
                self.assertNotIn("FUENTES DE INFORMACIÓN O EVIDENCIA", conteudo)
                self.assertNotIn("SOURCES OF INFORMATION OR EVIDENCE", conteudo)
                self.assertNotIn("Ferramentas utilizadas", conteudo)
                self.assertNotIn("Herramientas utilizadas", conteudo)
                self.assertNotIn("Tools used", conteudo)

    def test_multisselecao_aplica_ou_interno_e_e_entre_dimensoes(self):
        response = self.client.get(
            reverse("catalogo_experiencias"),
            {
                "efs": [self.efs_a.pk, self.efs_b.pk],
                "setor": [self.setor_a.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.publica_a.titulo)
        self.assertNotContains(response, self.publica_b.titulo)
        self.assertEqual(response.context["total_resultados"], 1)

    def test_parametros_invalidos_nao_provocam_erro(self):
        response = self.client.get(
            reverse("catalogo_experiencias"),
            {"efs": ["inválido", "-1"], "ano": ["texto", "2099"]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 2)

    def test_parametro_legado_de_ferramenta_nao_altera_os_quatro_filtros_oficiais(self):
        response = self.client.get(
            reverse("catalogo_experiencias"),
            {"ferramenta": "Matriz de critérios"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 2)
        self.assertContains(response, self.publica_a.titulo)
        self.assertContains(response, self.publica_b.titulo)

    def test_marcos_sao_biblioteca_com_busca_e_drawer_acessivel(self):
        response = self.client.get(
            reverse("normas_internacionais"), {"q": "verificável"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Biblioteca normativa")
        self.assertContains(response, self.norma.nome)
        self.assertContains(response, 'class="norm-dialog"')
        self.assertContains(response, "data-dialog-close")
        self.assertContains(response, 'data-add-filter="pais"')
        self.assertContains(response, 'name="setor"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertNotContains(response, "34 resultados")
        self.assertNotContains(response, "download=")
        self.assertNotContains(response, 'href="#"')
        for icon_name in ("account_circle", "contrast", "balance", "download", "search"):
            self.assertNotContains(response, f">{icon_name}<")

    def test_marcos_nao_derivam_filtros_de_pratica_publica(self):
        response = self.client.get(
            reverse("normas_internacionais"),
            {"pais": self.pais_a.pk, "setor": self.setor_a.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 0)
        self.assertNotContains(response, self.norma.nome)
        self.assertNotContains(response, self.norma_b.nome)

    def test_ferramentas_e_banco_nao_publicam_dados_demonstrativos(self):
        for nome in ("ferramentas", "banco_tecnico"):
            with self.subTest(nome=nome):
                response = self.client.get(reverse(nome))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["total_resultados"], 0)
                self.assertNotContains(
                    response,
                    "Roteiro demonstrativo que não deve ser publicado",
                )
                self.assertNotContains(response, "15 ferramentas")
                self.assertNotContains(response, 'href="#"')

    def test_estados_indisponiveis_sao_publicos_e_trilingues(self):
        casos = (
            (
                "/ferramentas/",
                "O cat&aacute;logo de ferramentas est&aacute; em prepara&ccedil;&atilde;o.",
                "Os conte&uacute;dos ser&atilde;o publicados ap&oacute;s a conclus&atilde;o da curadoria institucional.",
            ),
            (
                "/es/ferramentas/",
                "El cat&aacute;logo de herramientas est&aacute; en preparaci&oacute;n.",
                "Los contenidos se publicar&aacute;n despu&eacute;s de concluir la curadur&iacute;a institucional.",
            ),
            (
                "/en/ferramentas/",
                "The tools catalog is being prepared.",
                "Content will be published after institutional curation is complete.",
            ),
            (
                "/banco-tecnico/",
                "O Banco T&eacute;cnico est&aacute; em prepara&ccedil;&atilde;o.",
                "Documentos e refer&ecirc;ncias ser&atilde;o publicados ap&oacute;s a conclus&atilde;o da curadoria institucional.",
            ),
            (
                "/es/banco-tecnico/",
                "El Banco T&eacute;cnico est&aacute; en preparaci&oacute;n.",
                "Los documentos y referencias se publicar&aacute;n despu&eacute;s de concluir la curadur&iacute;a institucional.",
            ),
            (
                "/en/banco-tecnico/",
                "The Technical Bank is being prepared.",
                "Documents and references will be published after institutional curation is complete.",
            ),
        )
        for caminho, titulo, texto in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, texto, html=False)
                self.assertNotContains(response, "Fase 2C")
                self.assertNotContains(response, "Phase 2C")
                self.assertNotContains(response, "publication or origin marker")

    def test_compendio_sem_pdf_real_exibe_apenas_status_institucional(self):
        casos = (
            ("/normas-internacionais/", "Comp&ecirc;ndio institucional em prepara&ccedil;&atilde;o."),
            ("/es/normas-internacionais/", "Compendio institucional en preparaci&oacute;n."),
            ("/en/normas-internacionais/", "Institutional compendium in preparation."),
        )
        for caminho, texto in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                rendered = response.content.decode()

                self.assertContains(response, 'class="library-compendium-status"')
                self.assertContains(response, texto, html=False)
                self.assertNotRegex(
                    rendered,
                    r'<(?:a|button)[^>]*class="[^"]*library-compendium-status',
                )
                interactive_compendium = [
                    match.group(0)
                    for match in re.finditer(
                        r"<(?P<tag>a|button)\b[^>]*>.*?</(?P=tag)>",
                        rendered,
                        flags=re.IGNORECASE | re.DOTALL,
                    )
                    if re.search(
                        r"comp[eê]ndio|compendium", match.group(0), re.IGNORECASE
                    )
                ]
                self.assertEqual(interactive_compendium, [])
                self.assertNotContains(response, "Download PDF compendium")
                self.assertNotContains(response, "Descargar compendio en PDF")
                self.assertNotContains(
                    response, "Baixar comp&ecirc;ndio em PDF", html=False
                )
                self.assertNotContains(response, "download=")

    def test_toolbar_normativa_usa_grade_fluida_sem_larguras_fracionadas(self):
        css = Path(finders.find("praticas/css/marcos-publicos.css")).read_text(
            encoding="utf-8"
        )
        toolbar = css.split(".library-toolbar {", 1)[1].split("}", 1)[0]

        self.assertIn("minmax(260px, 2fr)", toolbar)
        self.assertIn("auto", toolbar)
        self.assertNotIn("291.729187px", css)
        self.assertIn(".library-compendium-status", css)
        self.assertNotIn(".library-compendium {", css)
        self.assertNotIn(".library-compendium-wrap", css)

    def test_assets_progressivos_dos_catalogos_existem(self):
        for asset in (
            "praticas/css/catalogo-publico.css",
            "praticas/css/marcos-publicos.css",
            "praticas/css/ferramentas-publicas.css",
            "praticas/js/filtros-publicos.js",
            "praticas/js/marcos-drawer.js",
        ):
            with self.subTest(asset=asset):
                self.assertIsNotNone(finders.find(asset))
