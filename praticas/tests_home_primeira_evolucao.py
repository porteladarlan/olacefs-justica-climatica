import re

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
        self.assertContains(response, 'class="nav-link nav-link-pending" role="link" aria-disabled="true"', html=False)
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
                self.assertContains(response, proposito, html=False)
                self.assertContains(response, "COMTEMA")
                self.assertContains(response, "CGID")
                self.assertContains(response, "GIZ")
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

        self.assertContains(response, "Uma mensagem da COMTEMA e da CGID")
        self.assertContains(response, "Dr. Camilo Ben&iacute;tez", html=False)
        self.assertContains(response, "Dra. Pamela Calletti")
        self.assertContains(response, f'src="{static("praticas/img/camilo-benitez.jpg")}"')
        self.assertContains(response, f'src="{static("praticas/img/pamela-calletti.jpg")}"')
        self.assertIsNone(re.search(r'<img[^>]+src=["\']https?://', html, re.IGNORECASE))

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
        self.assertEqual(len(re.findall(r"<h4\b", fundamentos)), 6)
        self.assertIsNone(re.search(r"<h(?:1|5|6)\b", fundamentos))
        self.assertIsNone(re.search(r"<h[2-4][^>]*>\s*</h[2-4]>", fundamentos))

    def test_estilos_de_foco_e_contraste_usam_cores_aprovadas(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertContains(response, "outline: 3px solid var(--purple-900) !important;")
        self.assertContains(response, "outline-offset: 3px !important;")
        self.assertContains(response, "box-shadow: none !important;")
        self.assertContains(response, "color: #4f706e;")
        self.assertNotContains(response, "#F2C230")
        self.assertContains(response, 'tab.addEventListener("shown.bs.tab", handleShown, { once: true });', count=1)
        self.assertContains(response, "bootstrap.Tab.getOrCreateInstance(tab).show();", count=1)
        self.assertContains(response, 'event.key === "Enter" || event.key === " "')

    def test_fundamentos_preservam_conteudo_nos_tres_idiomas(self):
        casos = [
            ("/", "Fundamentos e estrat&eacute;gias", "Participa&ccedil;&atilde;o nos benef&iacute;cios", "Estrat&eacute;gia de g&ecirc;nero"),
            ("/es/", "Fundamentos y estrategias", "Participaci&oacute;n en los beneficios", "Estrategia de g&eacute;nero"),
            ("/en/", "Foundations and strategies", "Benefit sharing", "Gender strategy"),
        ]

        for caminho, titulo, beneficio, genero in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, beneficio, html=False)
                self.assertContains(response, genero, html=False)

    def test_mapa_e_video_assumem_estado_futuro_sem_dados_falsos(self):
        casos = [
            ("/", "Mapa regional das EFS", "Etapa futura", "Conte&uacute;do audiovisual em prepara&ccedil;&atilde;o"),
            ("/es/", "Mapa regional de las EFS", "Etapa futura", "Contenido audiovisual en preparaci&oacute;n"),
            ("/en/", "Regional map of SAIs", "Future stage", "Audiovisual content in preparation"),
        ]

        for caminho, mapa, estado, video in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, mapa)
                self.assertContains(response, estado)
                self.assertContains(response, video, html=False)
                self.assertContains(response, f'href="{reverse("catalogo_experiencias")}"')
                self.assertContains(response, f'href="{reverse("normas_internacionais")}"')
