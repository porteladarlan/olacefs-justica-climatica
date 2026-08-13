import re
from pathlib import Path

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class HomePrimeiraEvolucaoTests(TestCase):
    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    def test_home_responde_e_usa_asset_institucional_local(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<section class="jc-hero home-block"', html=False)
        self.assertContains(response, f'src="{static("praticas/img/icone-jc.svg")}"')
        self.assertContains(response, "pessoas colaborando ao redor de uma balan&ccedil;a")

    def test_cabecalho_corresponde_ao_prototipo_sem_busca_legada(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")

        self.assertContains(response, "Plataforma de Justi&ccedil;a Clim&aacute;tica", html=False)
        self.assertContains(response, "Guia Viva &middot; CGID + COMTEMA", html=False)
        self.assertContains(response, f'href="{reverse("catalogo_experiencias")}"')
        self.assertContains(response, f'href="{reverse("normas_internacionais")}"')
        self.assertContains(response, "Boas Pr&aacute;ticas", html=False)
        self.assertContains(response, "Marcos Normativos")
        self.assertContains(response, "Ferramentas")
        self.assertContains(response, f'href="{reverse("ferramentas")}"')
        self.assertIsNone(re.search(r'class="[^"]*\bnav-link-pending\b', html))
        self.assertContains(response, f'href="{reverse("login_usuario")}"')
        self.assertContains(response, f'href="{reverse("registrar_usuario")}"')
        self.assertContains(response, f'href="{reverse("status_envio")}"')
        self.assertContains(response, 'id="languageSwitcher"')
        self.assertContains(response, 'id="highContrastToggle"')
        self.assertNotIn('id="buscaGlobal"', html)
        self.assertNotIn("nav-search-form", html)
        self.assertNotIn("data-home-tab-target", html)

    def test_hero_preserva_proposito_e_ctas_corretos_nos_tres_idiomas(self):
        casos = [
            ("/", "pr&aacute;tica do controle externo", "Explorar marcos normativos", "Ver mapa da regi&atilde;o"),
            ("/es/", "pr&aacute;ctica del control externo", "Explorar marcos normativos", "Ver mapa de la regi&oacute;n"),
            ("/en/", "external-control practice", "Explore normative frameworks", "View the regional map"),
        ]

        for caminho, proposito, cta_marcos, cta_mapa in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)

                html = response.content.decode("utf-8")
                hero = html.split(
                    '<section class="jc-hero home-block"',
                    1,
                )[1].split("</section>", 1)[0]

                self.assertContains(response, proposito, html=False)
                self.assertContains(response, "COMTEMA")
                self.assertContains(response, "CGID")
                self.assertNotIn("GIZ", hero)
                self.assertContains(response, cta_marcos, html=False)
                self.assertContains(response, cta_mapa, html=False)
                self.assertContains(response, f'href="{reverse("normas_internacionais")}"')
                self.assertContains(response, 'href="#mapSection"')

    def test_home_remove_grade_antiga_e_preserva_ordem_aprovada(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")

        self.assertNotIn("home-primary-access", html)
        self.assertNotIn("Banco T&eacute;cnico", html)
        self.assertNotIn("Dimens&otilde;es de Justi&ccedil;a Clim&aacute;tica", html)
        hero = html.index('class="jc-hero home-block"')
        mensagens = html.index('id="testimonialsSection"')
        fundamentos = html.index('id="pillarsSection"')
        mapa = html.index('id="mapSection"')
        video = html.index('id="videoSection"')
        self.assertLess(hero, mensagens)
        self.assertLess(mensagens, fundamentos)
        self.assertLess(fundamentos, mapa)
        self.assertLess(mapa, video)

    def test_mensagens_institucionais_usam_assets_locais(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")

        self.assertContains(response, "Palavras das Presid&ecirc;ncias da COMTEMA e da CGID")
        self.assertContains(response, "Dr. Camilo Ben&iacute;tez", html=False)
        self.assertContains(response, "Dra. Pamela Calletti")
        self.assertContains(response, f'src="{static("praticas/img/camilo-benitez.jpg")}"')
        self.assertContains(response, f'src="{static("praticas/img/pamela-calletti.jpg")}"')
        self.assertIsNone(re.search(r'<img[^>]+src=["\']https?://', html, re.IGNORECASE))
        self.assertLess(
            html.index("Dra. Pamela Calletti"),
            html.index("Dr. Camilo Ben&iacute;tez"),
        )

    def test_fundamentos_tem_exatamente_tres_abas_acessiveis(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertContains(response, '<button class="home-foundation-tab', count=3, html=False)
        self.assertContains(response, 'id="concepto-tab"')
        self.assertContains(response, 'id="controle-tab"')
        self.assertContains(response, 'id="genero-tab"')
        self.assertNotContains(response, 'id="normas-tab"')
        self.assertContains(response, 'id="concepto-pane" role="tabpanel" aria-labelledby="concepto-tab" tabindex="-1"', html=False)
        self.assertContains(response, 'id="controle-pane" role="tabpanel" aria-labelledby="controle-tab" tabindex="-1"', html=False)
        self.assertContains(response, 'id="genero-pane" role="tabpanel" aria-labelledby="genero-tab" tabindex="-1"', html=False)
        self.assertContains(response, f'src="{static("praticas/img/pilar-justicia.jpg")}"')
        self.assertContains(response, f'src="{static("praticas/img/pilar-control.jpg")}"')
        self.assertContains(response, f'src="{static("praticas/img/pilar-genero.jpg")}"')

    def test_fundamentos_preservam_hierarquia_de_titulos(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        fundamentos = html.split('<section class="home-foundations', 1)[1].split("</section>", 1)[0]

        self.assertEqual(len(re.findall(r"<h2\b", fundamentos)), 1)
        self.assertEqual(len(re.findall(r"<h3\b", fundamentos)), 3)
        self.assertEqual(len(re.findall(r"<h4\b", fundamentos)), 5)
        self.assertIsNone(re.search(r"<h(?:1|5|6)\b", fundamentos))
        self.assertIsNone(re.search(r"<h[2-4][^>]*>\s*</h[2-4]>", fundamentos))

    def test_home_carrega_estilo_proprio_e_preserva_foco_das_abas(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertContains(response, f'href="{static("praticas/css/home.css")}"')
        self.assertContains(response, 'role="tablist"')
        self.assertContains(response, 'aria-selected="true"')
        self.assertContains(response, 'id="concepto-pane" role="tabpanel" aria-labelledby="concepto-tab" tabindex="-1"', html=False)
        self.assertContains(response, 'tab.addEventListener("shown.bs.tab", handleShown, { once: true });', count=1)
        self.assertContains(response, "bootstrap.Tab.getOrCreateInstance(tab).show();", count=1)
        self.assertContains(response, 'event.key === "Enter" || event.key === " "')

    def test_home_usa_estados_roxos_sem_foco_amarelo(self):
        css = Path(finders.find("praticas/css/home.css")).read_text(
            encoding="utf-8"
        )

        self.assertRegex(
            css,
            r"\.home-foundation-tab\s*\{[^}]*background: var\(--lilac-pale\)",
        )
        self.assertRegex(
            css,
            r"\.home-foundation-tab\.active,[^{]+\{[^}]*background: var\(--purple\)",
        )
        self.assertRegex(
            css,
            r"\.home-map-country\.is-member\s*\{[^}]*fill: var\(--purple-soft\)",
        )
        self.assertRegex(
            css,
            r"\.home-map-country\.is-selected\s*\{[^}]*fill: var\(--purple\)",
        )
        self.assertIn(".home-map-country.is-coordinated", css)
        self.assertIn("outline: 3px solid var(--purple-mid);", css)
        self.assertNotIn("#f4b400", css.lower())
        self.assertNotIn("#ffd800", css.lower())
        self.assertNotIn("fill: #698D8B", css)

    def test_ctas_usam_position_paper_e_pagina_de_exemplos(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        fundamentos = html.split(
            '<section class="home-foundations', 1
        )[1].split("</section>", 1)[0]
        position_paper = (
            "https://olacefs.com/giz/wp-content/uploads/sites/14/2025/11/"
            "Position_Paper_Miolo_ESP.pdf"
        )

        self.assertEqual(
            fundamentos.count(f'href="{position_paper}"'),
            3,
        )
        self.assertEqual(
            fundamentos.count('target="_blank" rel="noopener noreferrer"'),
            3,
        )
        self.assertEqual(
            fundamentos.count(
                f'href="{reverse("exemplos_injustica_climatica")}"'
            ),
            3,
        )
        self.assertNotIn(f'href="{reverse("sobre_plataforma")}"', fundamentos)
        self.assertNotIn("#ejemplosModal", fundamentos)

    def test_caixas_conceituais_aparecem_antes_dos_ctas_em_todas_as_abas(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        fundamentos = html.split(
            '<section class="home-foundations', 1
        )[1].split("</section>", 1)[0]

        for pane_id in ("concepto-pane", "controle-pane", "genero-pane"):
            with self.subTest(pane_id=pane_id):
                painel = fundamentos.split(f'id="{pane_id}"', 1)[1]
                if pane_id == "concepto-pane":
                    self.assertLess(
                        painel.index('class="home-foundation-introduction"'),
                        painel.index('class="home-foundation-concept-layout"'),
                    )
                    self.assertLess(
                        painel.index('class="home-foundation-concept-layout"'),
                        painel.index('class="home-foundation-actions"'),
                    )
                else:
                    self.assertLess(
                        painel.index('class="home-foundation-top"'),
                        painel.index('class="home-foundation-actions"'),
                    )
                if pane_id == "controle-pane":
                    self.assertLess(
                        painel.index('class="home-foundation-strategies"'),
                        painel.index('class="home-foundation-actions"'),
                    )

    def test_primeira_aba_tem_layout_e_ordem_equivalentes_nos_tres_idiomas(self):
        casos = (
            (
                "/",
                "Equidade e Inclusão",
                "Responsabilidades comuns, mas compartilhadas",
                "Participação Social",
            ),
            (
                "/es/",
                "Equidad e Inclusión",
                "Responsabilidades comunes, pero compartidas",
                "Participación Social",
            ),
            (
                "/en/",
                "Equity and Inclusion",
                "Common but shared responsibilities",
                "Social Participation",
            ),
        )

        for caminho, primeiro, segundo, terceiro in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode("utf-8")
                painel = html.split('id="concepto-pane"', 1)[1].split(
                    'id="controle-pane"', 1
                )[0]

                self.assertEqual(
                    painel.count('class="home-foundation-strategy"'),
                    3,
                )
                self.assertIn('class="home-foundation-introduction"', painel)
                self.assertIn('class="home-foundation-concept-layout"', painel)
                self.assertEqual(
                    painel.count(static("praticas/img/pilar-justicia.jpg")),
                    1,
                )
                self.assertLess(painel.index(primeiro), painel.index(segundo))
                self.assertLess(painel.index(segundo), painel.index(terceiro))
                self.assertLess(
                    painel.index('class="home-foundation-strategies"'),
                    painel.index(
                        'class="home-foundation-photo home-foundation-concept-photo"'
                    ),
                )

        css = Path(finders.find("praticas/css/home.css")).read_text(
            encoding="utf-8"
        )
        self.assertRegex(
            css,
            r"\.home-foundation-concept-layout\s*\{[^}]*"
            r"grid-template-columns:\s*minmax\(0, 1fr\)\s+minmax\(0, 1\.02fr\)",
        )
        responsivo = css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".home-design .home-foundation-concept-layout,", responsivo)
        self.assertRegex(
            responsivo,
            r"\.home-foundation-concept-photo img\s*\{[^}]*height:\s*auto",
        )

    def test_texto_negocial_portugues_e_integralmente_renderizado(self):
        response = self.client.get(reverse("pagina_inicial"))

        trechos = (
            "Justiça climática é uma abordagem que integra os Direitos Humanos, "
            "a justiça social e proteção ambiental",
            "Equidade e Inclusão",
            "Não apenas, minimizar impactos negativos das mudanças climáticas",
            "Participação Social",
            "Incorporar a consulta, envolvimento e participação efetiva",
            "Responsabilidades comuns, mas compartilhadas",
            "a responsabilidade pelo enfrentamento da mudança do clima é comum, "
            "porém diferenciada",
        )
        for trecho in trechos:
            with self.subTest(trecho=trecho):
                self.assertContains(response, trecho)

    def test_home_nao_renderiza_modal_legado_de_exemplos(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertNotContains(response, 'id="ejemplosModal"')
        self.assertNotContains(response, 'data-bs-target="#ejemplosModal"')

    def test_fundamentos_preservam_conteudo_nos_tres_idiomas(self):
        casos = [
            ("/", "Fundamentos e estratégias", "Equidade e Inclusão", "Estratégia de gênero"),
            ("/es/", "Fundamentos y estrategias", "Equidad e Inclusión", "Estrategia de género"),
            ("/en/", "Foundations and strategies", "Equity and Inclusion", "Gender strategy"),
        ]

        for caminho, titulo, beneficio, genero in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, beneficio, html=False)
                self.assertContains(response, genero, html=False)

    def test_home_preserva_textos_institucionais_existentes_em_es_e_en(self):
        casos = (
            (
                "/es/",
                "La justicia climática es un enfoque que integra los Derechos "
                "Humanos, la justicia social y la protección ambiental",
            ),
            (
                "/en/",
                "Climate justice is an approach that integrates Human Rights, "
                "social justice and environmental protection",
            ),
        )

        for caminho, trecho in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, trecho)

    def test_pagina_de_exemplos_e_publica_trilingue_e_usa_acervo_oficial(self):
        casos = (
            ("/exemplos-injustica-climatica/", "Exemplos de injustiça climática"),
            ("/es/exemplos-injustica-climatica/", "Ejemplos de injusticia climática"),
            ("/en/exemplos-injustica-climatica/", "Examples of climate injustice"),
        )

        for caminho, titulo in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo)
                self.assertContains(response, "OLACEFS + GIZ")
                self.assertContains(response, "Gustavo Mansur / Agência Senado")
                self.assertContains(response, "FAO (2019)")
                self.assertContains(response, "Denisa Starbova")
                self.assertContains(
                    response,
                    'src="/static/praticas/img/ejemplo-rs2024.jpg"',
                )
                self.assertContains(
                    response,
                    'src="/static/praticas/img/ejemplo-corredor-seco.jpg"',
                )
                self.assertContains(
                    response,
                    'src="/static/praticas/img/ejemplo-huni-kui.jpg"',
                )

    def test_pagina_de_exemplos_tem_breadcrumb_e_hierarquia_semantica(self):
        response = self.client.get(reverse("exemplos_injustica_climatica"))
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="Navegação estrutural"')
        self.assertContains(response, f'href="{reverse("pagina_inicial")}"')
        self.assertContains(
            response,
            f'href="{reverse("pagina_inicial")}#pillarsSection"',
        )
        self.assertEqual(len(re.findall(r"<h1\b", html)), 1)
        self.assertGreaterEqual(len(re.findall(r"<h2\b", html)), 4)

    def test_mapa_funcional_e_video_oficial_trilingue(self):
        casos = [
            ("/", "EFS da Am&eacute;rica Latina e Caribe", "Mapa interativo", "Teaser da Plataforma de Justi&ccedil;a Clim&aacute;tica"),
            ("/es/", "EFS de Am&eacute;rica Latina y el Caribe", "Mapa interactivo", "Teaser de la Plataforma de Justicia Clim&aacute;tica"),
            ("/en/", "SAIs of Latin America and the Caribbean", "Interactive map", "Climate Justice Platform Teaser"),
        ]

        for caminho, mapa, estado_funcional, video in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, mapa, html=False)
                self.assertContains(response, estado_funcional)
                self.assertContains(response, video, html=False)
                self.assertNotContains(response, "Etapa futura")
                self.assertNotContains(response, "Future stage")
                self.assertContains(response, f'formaction="{reverse("catalogo_experiencias")}"')
                self.assertContains(response, f'formaction="{reverse("normas_internacionais")}"')

    def test_video_home_usa_player_html5_via_media_sem_autoplay(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        bloco = html.split('<section class="home-video', 1)[1].split(
            "</section>", 1
        )[0]

        self.assertIn("<video", bloco)
        self.assertIn("controls", bloco)
        self.assertIn('preload="metadata"', bloco)
        self.assertIn("playsinline", bloco)
        self.assertIn(
            '<source src="/media/videos/teaser-plataforma-jc.mp4" type="video/mp4">',
            bloco,
        )
        self.assertNotIn("autoplay", bloco)
        self.assertNotIn("Conte&uacute;do audiovisual em prepara&ccedil;&atilde;o", bloco)
        self.assertNotIn("static/praticas", bloco)
        self.assertIn(
            'class="home-video-fallback" id="home-video-error" role="status" hidden',
            bloco,
        )

        pagina = response.content.decode("utf-8")
        self.assertIn('player.addEventListener("error"', pagina)
        self.assertIn("errorMessage.hidden = false;", pagina)
