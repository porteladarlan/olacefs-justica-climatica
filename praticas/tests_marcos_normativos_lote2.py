import json
from copy import deepcopy
from html import unescape
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

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
from .views import MARCOS_NATUREZA_FILTROS, MARCOS_SETOR_FILTROS


class _SelectParser(HTMLParser):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.options = []
        self._inside = False
        self._current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "select" and attrs.get("name") == self.name:
            self._inside = True
        elif self._inside and tag == "option":
            self._current = [attrs.get("value", ""), ""]

    def handle_data(self, data):
        if self._current is not None:
            self._current[1] += data

    def handle_endtag(self, tag):
        if tag == "option" and self._current is not None:
            self.options.append((self._current[0], self._current[1].strip()))
            self._current = None
        elif tag == "select" and self._inside:
            self._inside = False


def _select_options(response, name):
    parser = _SelectParser(name)
    parser.feed(response.content.decode("utf-8"))
    if not parser.options:
        raise AssertionError(f"select {name!r} não encontrado ou vazio")
    return parser.options


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
            nome_en="Binding framework",
            ano=2018,
            ano_texto="2018",
            natureza_juridica="Vinculante",
            natureza_juridica_es="Vinculante",
            natureza_juridica_en="Binding",
            setores_aplicaveis="Água e Energia, Infraestrutura, Biodiversidade e Ecossistemas, Saúde, Alimentação e Agricultura, Indústria Extrativa, Gestão de Riscos e Desastres, Gênero e direitos humanos, Pobreza e desigualdade",
            setores_aplicaveis_es="Agua y Energía, Infraestructura, Biodiversidad y Ecosistemas, Salud, Alimentación y Agricultura, Industria Extractiva, Gestión de Riesgo y Desastres, Género y derechos humanos, Pobreza y desigualdad",
            setores_aplicaveis_en="Water and Energy, Infrastructure, Biodiversity and Ecosystems, Health, Food and Agriculture, Extractive Industry, Disaster Risk Management, Gender and human rights, Poverty and inequality",
            cobertura_paises_es="Cobertura institucional do marco.",
            resumo_es="Introducción institucional aprobada.",
            url_referencia="https://example.org/fonte-oficial",
            ficha_tecnica_url="https://example.org/ficha-tecnica",
        )
        cls.nao_vinculante = NormaInternacional.objects.create(
            nome="Marco não vinculante",
            nome_es="Marco no vinculante",
            nome_en="Non-binding framework",
            natureza_juridica="Não vinculante",
            natureza_juridica_es="No vinculante",
            natureza_juridica_en="Non-binding",
            setores_aplicaveis="Saúde",
            setores_aplicaveis_es="Salud",
            setores_aplicaveis_en="Health",
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
            {"natureza": "binding"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 1)
        self.assertContains(response, 'name="natureza"')
        self.assertContains(response, 'value="binding" selected')
        self.assertContains(response, self.vinculante.nome)
        self.assertNotContains(response, self.nao_vinculante.nome)

    def test_filtros_exibem_apenas_opcoes_canonicas_localizadas(self):
        casos = (
            ("/normas-internacionais/", 0),
            ("/es/normas-internacionais/", 1),
            ("/en/normas-internacionais/", 2),
        )
        for caminho, indice in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                setores = [(valor, unescape(rotulo).strip()) for valor, rotulo in _select_options(response, "setor") if valor]
                naturezas = [(valor, unescape(rotulo).strip()) for valor, rotulo in _select_options(response, "natureza") if valor]
                setores_esperados = sorted(MARCOS_SETOR_FILTROS, key=lambda item: item[1][indice].casefold())
                naturezas_esperadas = sorted(MARCOS_NATUREZA_FILTROS, key=lambda item: item[1][indice].casefold())
                self.assertEqual([valor for valor, _ in setores], [chave for chave, _ in setores_esperados])
                self.assertEqual([valor for valor, _ in naturezas], [chave for chave, _ in naturezas_esperadas])
                self.assertEqual([rotulo for _, rotulo in setores], [rotulos[indice] for _, rotulos in setores_esperados])
                self.assertEqual([rotulo for _, rotulo in naturezas], [rotulos[indice] for _, rotulos in naturezas_esperadas])
                foreign = [rotulo[indice_estrangeiro] for _, rotulo in MARCOS_SETOR_FILTROS for indice_estrangeiro in range(3) if indice_estrangeiro != indice]
                self.assertFalse(set(foreign) & {rotulo for _, rotulo in setores})

    def test_placeholders_dos_filtros_sao_localizados(self):
        casos = (
            ("/normas-internacionais/", "Todos os setores", "Toda natureza jurídica"),
            ("/es/normas-internacionais/", "Todos los sectores", "Toda naturaleza jurídica"),
            ("/en/normas-internacionais/", "All sectors", "All legal natures"),
        )
        for caminho, setor_esperado, natureza_esperada in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                for nome, esperado in (("setor", setor_esperado), ("natureza", natureza_esperada)):
                    with self.subTest(nome=nome):
                        opcoes = _select_options(response, nome)
                        placeholders = [rotulo for valor, rotulo in opcoes if valor == ""]
                        self.assertEqual(placeholders, [esperado])
                        self.assertEqual(sum(valor == "" for valor, _ in opcoes), 1)

    def test_filtros_aceitam_chaves_e_rotulos_legados(self):
        for idioma, valores in (
            ("pt-br", ("agua_energia", "Agua y Energía")),
            ("es", ("agua_energia", "Agua y Energía")),
            ("en", ("agua_energia", "Water and Energy")),
        ):
            with self.subTest(idioma=idioma):
                with translation.override(idioma):
                    for valor in valores:
                        response = self.client.get(reverse("normas_internacionais"), {"setor": valor})
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(response.context["total_resultados"], 1)
        for idioma, rotulo in (
            ("pt-br", "Vinculante"),
            ("es", "Vinculante"),
            ("en", "Binding"),
        ):
            with self.subTest(idioma=idioma):
                with translation.override(idioma):
                    response = self.client.get(reverse("normas_internacionais"), {"natureza": rotulo})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.context["total_resultados"], 1)

    def test_filtros_desconhecidos_sao_ignorados(self):
        response = self.client.get(
            reverse("normas_internacionais"),
            {"setor": "setores_aplicaveis__icontains=Vinculante", "natureza": "desconhecida"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 2)
        self.assertEqual(response.context["setor_selecionado"], "")
        self.assertEqual(response.context["natureza_selecionada"], "")

    def test_todas_as_naturezas_canonicas_filtram_no_campo_atual(self):
        for idioma, campo, valores in (
            ("pt-br", "natureza_juridica", ("binding", "non_binding")),
            ("es", "natureza_juridica_es", ("binding", "non_binding")),
            ("en", "natureza_juridica_en", ("binding", "non_binding")),
        ):
            with self.subTest(idioma=idioma):
                with translation.override(idioma):
                    for valor in valores:
                        esperado = NormaInternacional.objects.filter(
                            **{campo: dict(MARCOS_NATUREZA_FILTROS)[valor][{"pt-br": 0, "es": 1, "en": 2}[idioma]]}
                        ).count()
                        response = self.client.get(reverse("normas_internacionais"), {"natureza": valor})
                        self.assertEqual(response.context["total_resultados"], esperado)

    def test_todos_os_rotulos_legados_de_natureza_mapeiam_para_chave_canonica(self):
        casos = (
            ("pt-br", "Vinculante", "binding"),
            ("pt-br", "Não vinculante", "non_binding"),
            ("es", "No vinculante", "non_binding"),
            ("en", "Binding", "binding"),
            ("en", "Non-binding", "non_binding"),
        )
        for idioma, legado, chave in casos:
            with self.subTest(idioma=idioma, legado=legado):
                with translation.override(idioma):
                    response = self.client.get(reverse("normas_internacionais"), {"natureza": legado})
                self.assertContains(response, f'value="{chave}" selected')
                self.assertEqual(response.context["natureza_selecionada"], chave)

    def test_matriz_de_setores_e_derivada_da_fonte_operacional(self):
        fonte = Path(__file__).resolve().parent / "data" / "marcos_normativos_lote2.json"
        dados = json.loads(fonte.read_text(encoding="utf-8"))
        trios = {}
        for marco in dados["marcos"]:
            for setor in marco["setores_aplicaveis"]:
                trio = tuple(setor[idioma].strip() for idioma in ("pt", "es", "en"))
                self.assertNotIn("", trio)
                trios[trio] = None
        self.assertEqual(len(trios), 9)
        self.assertEqual(len({trio[0] for trio in trios}), 9)
        self.assertEqual(len({trio[1] for trio in trios}), 9)
        self.assertEqual(len({trio[2] for trio in trios}), 9)
        matriz_declarada = {tuple(rotulos) for _, rotulos in MARCOS_SETOR_FILTROS}
        self.assertEqual(set(trios), matriz_declarada)
        self.assertEqual(len(matriz_declarada), 9)

    def test_filtros_combinados_preservam_resultado_e_chips_localizados(self):
        response = self.client.get(
            reverse("normas_internacionais"),
            {
                "q": "Marco vinculante",
                "pais": self.brasil.pk,
                "setor": "agua_energia",
                "natureza": "binding",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 1)
        self.assertContains(response, self.vinculante.nome)
        self.assertNotContains(response, self.nao_vinculante.nome)
        self.assertContains(response, "Água e Energia")
        self.assertNotIn("agua_energia", {chip["rotulo"] for chip in response.context["chips_filtros"]})
        self.assertContains(response, "Vinculante")
        self.assertContains(response, "q=Marco+vinculante")
        self.assertContains(response, f"pais={self.brasil.pk}")

    def test_entradas_invalidas_nao_alteram_opcoes_nem_geram_erro(self):
        valores = ("", "x" * 161, "setores_aplicaveis__icontains=", '<script>alert(1)</script>')
        for valor in valores:
            with self.subTest(valor=valor):
                response = self.client.get(reverse("normas_internacionais"), {"setor": valor, "natureza": valor})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["setor_selecionado"], "")
                self.assertEqual(response.context["natureza_selecionada"], "")
                self.assertNotContains(response, "<script>alert(1)</script>", html=False)

    def test_paises_continuam_unicos_e_localizados(self):
        response = self.client.get(reverse("normas_internacionais"))
        paises = [item for item in response.context["paises"]]
        self.assertEqual(len(paises), len({pais.pk for pais in paises}))
        self.assertContains(response, self.brasil.nome)

    def test_consulta_usa_exclusivamente_o_campo_do_idioma_atual(self):
        armadilha = NormaInternacional.objects.create(
            nome="Armadilha de isolamento",
            nome_es="Trampa de aislamiento",
            nome_en="Isolation trap",
            natureza_juridica="Vinculante",
            natureza_juridica_es="No vinculante",
            natureza_juridica_en="Binding",
            setores_aplicaveis="Água e Energia",
            setores_aplicaveis_es="Salud",
            setores_aplicaveis_en="Infrastructure",
        )
        casos_estrangeiros = (
            ("/normas-internacionais/", "saude", False),
            ("/es/normas-internacionais/", "agua_energia", False),
            ("/en/normas-internacionais/", "agua_energia", False),
        )
        for caminho, setor, presente in casos_estrangeiros:
            with self.subTest(caminho=caminho, setor=setor):
                response = self.client.get(caminho, {"setor": setor})
                self.assertEqual(response.status_code, 200)
                nomes = {norma.nome for norma in response.context["normas"]}
                self.assertEqual(armadilha.nome in nomes, presente)
        for caminho, setor in (
            ("/normas-internacionais/", "agua_energia"),
            ("/es/normas-internacionais/", "saude"),
            ("/en/normas-internacionais/", "infraestrutura"),
        ):
            with self.subTest(caminho=caminho, setor=setor):
                response = self.client.get(caminho, {"setor": setor})
                self.assertIn(armadilha.nome, {norma.nome for norma in response.context["normas"]})

        casos_natureza_estrangeiros = (
            ("/normas-internacionais/", "non_binding", False),
            ("/es/normas-internacionais/", "binding", False),
            ("/en/normas-internacionais/", "non_binding", False),
        )
        for caminho, natureza, presente in casos_natureza_estrangeiros:
            with self.subTest(caminho=caminho, natureza=natureza):
                response = self.client.get(caminho, {"natureza": natureza})
                self.assertEqual(armadilha.pk in {norma.pk for norma in response.context["normas"]}, presente)
        for caminho, natureza in (
            ("/normas-internacionais/", "binding"),
            ("/es/normas-internacionais/", "non_binding"),
            ("/en/normas-internacionais/", "binding"),
        ):
            with self.subTest(caminho=caminho, natureza=natureza):
                response = self.client.get(caminho, {"natureza": natureza})
                self.assertIn(armadilha.pk, {norma.pk for norma in response.context["normas"]})
        for caminho, params in (
            ("/normas-internacionais/", {"setor": "agua_energia", "natureza": "binding"}),
            ("/es/normas-internacionais/", {"setor": "saude", "natureza": "non_binding"}),
            ("/en/normas-internacionais/", {"setor": "infraestrutura", "natureza": "binding"}),
        ):
            with self.subTest(caminho=caminho, params=params):
                response = self.client.get(caminho, params)
                self.assertIn(armadilha.pk, {norma.pk for norma in response.context["normas"]})

    def test_query_canonica_preserva_chaves_e_rotulos_na_troca_de_idioma(self):
        casos = (
            ("/normas-internacionais/", "Saúde", "Não vinculante"),
            ("/es/normas-internacionais/", "Salud", "No vinculante"),
            ("/en/normas-internacionais/", "Health", "Non-binding"),
        )
        for caminho, setor_label, natureza_label in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho, {"setor": "saude", "natureza": "non_binding"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["setor_selecionado"], "saude")
                self.assertEqual(response.context["natureza_selecionada"], "non_binding")
                selects = dict(_select_options(response, "setor"))
                natures = dict(_select_options(response, "natureza"))
                self.assertEqual(selects["saude"], setor_label)
                self.assertEqual(natures["non_binding"], natureza_label)
                labels = {chip["rotulo"] for chip in response.context["chips_filtros"]}
                self.assertIn(setor_label, labels)
                self.assertIn(natureza_label, labels)
                self.assertNotIn("saude", labels)
                self.assertNotIn("non_binding", labels)

    def test_urls_de_remocao_dos_chips_preservam_apenas_os_outros_parametros(self):
        response = self.client.get(
            reverse("normas_internacionais"),
            {"q": "Marco", "pais": self.brasil.pk, "setor": "saude", "natureza": "non_binding"},
        )
        chips = {chip["rotulo"]: parse_qs(urlsplit(chip["url_remover"]).query) for chip in response.context["chips_filtros"]}
        self.assertEqual(set(chips), {"Marco", "Brasil", "Saúde", "Não vinculante"})
        esperado = {"q": ["Marco"], "pais": [str(self.brasil.pk)], "setor": ["saude"], "natureza": ["non_binding"]}
        self.assertEqual(chips["Saúde"], {"q": ["Marco"], "pais": [str(self.brasil.pk)], "natureza": ["non_binding"]})
        self.assertEqual(chips["Não vinculante"], {"q": ["Marco"], "pais": [str(self.brasil.pk)], "setor": ["saude"]})
        self.assertEqual(chips["Brasil"], {"q": ["Marco"], "setor": ["saude"], "natureza": ["non_binding"]})
        self.assertEqual(chips["Marco"], {"pais": [str(self.brasil.pk)], "setor": ["saude"], "natureza": ["non_binding"]})
        self.assertEqual(set(esperado) - set(chips["Saúde"]), {"setor"})

    def test_pais_e_exibido_localizado_nas_rotas_dos_idiomas(self):
        for idioma, caminho, esperado in (
            ("pt-br", "/normas-internacionais/", "Brasil"),
            ("es", "/es/normas-internacionais/", "Brasil"),
            ("en", "/en/normas-internacionais/", "Brazil"),
        ):
            with self.subTest(idioma=idioma):
                with translation.override(idioma):
                    response = self.client.get(caminho)
                    paises = list(response.context["paises"])
                    self.assertEqual(len(paises), len({pais.pk for pais in paises}))
                    self.assertIn(esperado, {pais.nome_exibicao for pais in paises})

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

    def test_compendio_sem_pdf_final_exibe_status_nao_interativo(self):
        response = self.client.get(reverse("normas_internacionais"))
        rendered = response.content.decode()

        self.assertContains(
            response,
            "Comp&ecirc;ndio institucional em prepara&ccedil;&atilde;o.",
            html=False,
        )
        self.assertContains(response, '<p class="library-compendium-status">')
        self.assertNotRegex(
            rendered,
            r'<(?:a|button)[^>]*class="[^"]*library-compendium-status',
        )
        self.assertNotContains(response, "Baixar comp&ecirc;ndio em PDF", html=False)
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
            ids["ACORDO DE PARIS"],
            NormaInternacional.objects.get(nome="ACORDO DE PARIS").pk,
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

    def test_validacao_de_natureza_juridica_respeita_cada_idioma(self):
        casos = (
            ("natureza_juridica_pt", "No vinculante"),
            ("natureza_juridica_es", "Não vinculante"),
            ("natureza_juridica_en", "Não-binding"),
        )
        for campo, valor in casos:
            with self.subTest(campo=campo):
                marcos = deepcopy(self._dados())
                marcos[0][campo] = valor
                with self.assertRaises(CommandError):
                    Command()._validar(marcos)
