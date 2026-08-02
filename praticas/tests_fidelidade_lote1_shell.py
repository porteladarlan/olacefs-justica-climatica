import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import translation

from .models import EFS, Experiencia, Pais, Setor, TipoExperiencia


class ElementCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class ShellGlobalLote1Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.usuario = user_model.objects.create_user(
            username="usuario-shell",
            password="senha-teste-shell",
            first_name='<img src=x onerror="alert(1)">',
        )
        cls.staff = user_model.objects.create_user(
            username="staff-shell",
            password="senha-teste-shell",
            is_staff=True,
        )
        cls.superuser = user_model.objects.create_superuser(
            username="super-shell",
            email="super-shell@example.org",
            password="senha-teste-shell",
        )
        pais = Pais.objects.create(
            nome="Brasil",
            nome_es="Brasil",
            nome_en="Brazil",
            sigla="BRA-SHELL",
        )
        efs = EFS.objects.create(
            nome="EFS Shell",
            nome_es="EFS Shell",
            nome_en="SAI Shell",
            sigla="EFS-SHELL",
            pais=pais,
        )
        tipo = TipoExperiencia.objects.create(
            nome="Auditoria Shell",
            nome_es="Auditoría Shell",
            nome_en="Shell Audit",
        )
        setor = Setor.objects.create(
            nome="Setor Shell",
            nome_es="Sector Shell",
            nome_en="Shell Sector",
        )
        cls.experiencia = Experiencia.objects.create(
            autor=cls.usuario,
            titulo="Experiência pública do shell",
            titulo_es="Experiencia pública del shell",
            titulo_en="Public shell experience",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            ano_execucao=2026,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=setor,
            descricao="Experiência usada somente para validar o shell.",
            descricao_es="Experiencia usada solamente para validar el shell.",
            descricao_en="Experience used only to validate the shell.",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    def shell_html(self, response):
        html = response.content.decode("utf-8")
        return html.split('<nav class="navbar ', 1)[1].split("</nav>", 1)[0]

    def shell_elements(self, response):
        parser = ElementCollector()
        parser.feed("<nav " + self.shell_html(response))
        return parser.elements

    def current_elements(self, response):
        return [
            (tag, attrs)
            for tag, attrs in self.shell_elements(response)
            if attrs.get("aria-current") == "page"
        ]

    def source(self, relative_path):
        return (Path(settings.BASE_DIR) / relative_path).read_text(encoding="utf-8")

    def static_source(self, static_path):
        path = finders.find(static_path)
        self.assertIsNotNone(path)
        return Path(path).read_text(encoding="utf-8")

    def test_shell_exibe_marca_navegacao_e_rotulos_em_pt_es_en(self):
        cases = [
            ("/", "Plataforma de Justiça Climática", "Guia Viva · CGID + COMTEMA", "Boas Práticas", "Ferramentas"),
            ("/es/", "Plataforma de Justicia Climática", "Guía Viva · CGID + COMTEMA", "Buenas Prácticas", "Herramientas"),
            ("/en/", "Climate Justice Platform", "Living Guide · CGID + COMTEMA", "Good Practices", "Tools"),
        ]
        for path, brand, caption, practices, tools in cases:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                shell = unescape(re.sub(r"<[^>]+>", " ", self.shell_html(response)))
                self.assertIn(brand, shell)
                self.assertIn(caption, shell)
                self.assertIn(practices, shell)
                self.assertIn(tools, shell)

    def test_marca_aponta_para_home_e_e_atual_somente_na_home(self):
        response = self.client.get(reverse("pagina_inicial"))
        current = self.current_elements(response)
        self.assertEqual(len(current), 1)
        tag, attrs = current[0]
        self.assertEqual(tag, "a")
        self.assertEqual(attrs["href"], reverse("pagina_inicial"))
        self.assertIn("brand-lockup", attrs["class"])

    def test_destinos_reais_do_cabecalho(self):
        response = self.client.get(reverse("pagina_inicial"))
        shell = self.shell_html(response)
        for url_name in (
            "pagina_inicial",
            "catalogo_experiencias",
            "normas_internacionais",
            "ferramentas",
            "login_usuario",
            "registrar_usuario",
            "status_envio",
        ):
            with self.subTest(url_name=url_name):
                self.assertIn(f'href="{reverse(url_name)}"', shell)

        self.client.force_login(self.staff)
        staff_shell = self.shell_html(self.client.get(reverse("pagina_inicial")))
        for url_name in (
            "meus_envios",
            "favoritos_experiencias",
            "painel_revisao",
            "painel_revisao_edicoes",
            "admin:index",
        ):
            with self.subTest(staff_url_name=url_name):
                self.assertIn(f'href="{reverse(url_name)}"', staff_shell)

    def test_ferramentas_tem_rota_publica_real_e_interativa(self):
        for path, label in (("/", "Ferramentas"), ("/es/", "Herramientas"), ("/en/", "Tools")):
            with self.subTest(path=path):
                response = self.client.get(path)
                shell = self.shell_html(response)
                tools_links = [
                    attrs
                    for tag, attrs in self.shell_elements(response)
                    if tag == "a" and attrs.get("href") == reverse("ferramentas")
                ]
                self.assertEqual(len(tools_links), 1)
                self.assertIn(label, unescape(re.sub(r"<[^>]+>", " ", shell)))
                self.assertNotIn("nav-link-pending", shell)

        with translation.override("pt-br"):
            ferramentas_url = reverse("ferramentas")
            self.assertEqual(resolve(ferramentas_url).url_name, "ferramentas")
            self.assertEqual(self.client.get(ferramentas_url).status_code, 200)

    def test_boas_praticas_e_o_unico_estado_atual_em_suas_rotas(self):
        routes = [
            reverse("catalogo_experiencias"),
            reverse("detalhe_experiencia", args=[self.experiencia.pk]),
            reverse("comparar_experiencias"),
            reverse("favoritos_experiencias"),
        ]
        for path in routes:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                current = self.current_elements(response)
                self.assertEqual(len(current), 1)
                self.assertEqual(current[0][1]["href"], reverse("catalogo_experiencias"))

    def test_marcos_e_o_unico_estado_atual_em_normas(self):
        response = self.client.get(reverse("normas_internacionais"))
        self.assertEqual(response.status_code, 200)
        current = self.current_elements(response)
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0][1]["href"], reverse("normas_internacionais"))

    def test_meu_espaco_ativo_em_login_e_cadastro(self):
        for url_name in ("login_usuario", "registrar_usuario"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                current = self.current_elements(response)
                self.assertEqual(len(current), 1)
                self.assertEqual(current[0][1]["href"], reverse(url_name))
                self.assertIn("header-space-button nav-section-current", self.shell_html(response))

    def test_meu_espaco_ativo_em_rotas_autenticadas_relacionadas(self):
        self.client.force_login(self.usuario)
        for url_name in ("meus_envios", "status_envio"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                current = self.current_elements(response)
                self.assertEqual(len(current), 1)
                self.assertEqual(current[0][1]["href"], reverse(url_name))
                self.assertIn("header-space-button nav-section-current", self.shell_html(response))

        response = self.client.get(reverse("adicionar_boa_pratica"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.current_elements(response), [])
        self.assertIn("header-space-button nav-section-current", self.shell_html(response))

        self.client.force_login(self.staff)
        for url_name in ("painel_revisao", "painel_revisao_edicoes"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(self.current_elements(response)), 1)
                self.assertIn("header-space-button nav-section-current", self.shell_html(response))

    def test_menu_anonimo_usa_textos_neutros_e_destinos_reais(self):
        shell = unescape(self.shell_html(self.client.get(reverse("pagina_inicial"))))
        self.assertIn("Acesse sua conta", shell)
        self.assertIn("Crie sua conta na plataforma", shell)
        self.assertNotIn("conta institucional", shell.lower())
        self.assertNotIn("sua EFS", shell)
        self.assertNotIn("Meus envios", shell)
        self.assertNotIn("Painel de revisão", shell)
        self.assertNotIn("Administração do Django", shell)
        self.assertNotIn(f'href="{reverse("logout_usuario")}"', shell)

    def test_menu_autenticado_exibe_usuario_escapado_e_destinos_reais(self):
        self.client.force_login(self.usuario)
        shell = self.shell_html(self.client.get(reverse("pagina_inicial")))
        self.assertIn("&lt;img", shell)
        self.assertNotIn('<img src=x onerror="alert(1)">', shell)
        self.assertIn(f'href="{reverse("meus_envios")}"', shell)
        self.assertIn(f'href="{reverse("status_envio")}"', shell)
        self.assertIn(f'href="{reverse("favoritos_experiencias")}"', shell)
        self.assertIn(f'href="{reverse("logout_usuario")}"', shell)
        self.assertNotIn(f'href="{reverse("login_usuario")}"', shell)
        self.assertNotIn(f'href="{reverse("registrar_usuario")}"', shell)

    def test_itens_de_revisao_e_admin_sao_exclusivos_de_staff(self):
        self.client.force_login(self.usuario)
        ordinary_shell = self.shell_html(self.client.get(reverse("pagina_inicial")))
        self.assertNotIn(f'href="{reverse("painel_revisao")}"', ordinary_shell)
        self.assertNotIn(f'href="{reverse("admin:index")}"', ordinary_shell)

        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                staff_shell = self.shell_html(self.client.get(reverse("pagina_inicial")))
                self.assertIn(f'href="{reverse("painel_revisao")}"', staff_shell)
                self.assertIn(f'href="{reverse("painel_revisao_edicoes")}"', staff_shell)
                self.assertIn(f'href="{reverse("admin:index")}"', staff_shell)

    def test_seletor_de_idioma_tem_allowlist_e_opcao_atual(self):
        for path, selected_value, label in (
            ("/", "pt-br", "Selecionar idioma"),
            ("/es/", "es", "Seleccionar idioma"),
            ("/en/", "en", "Select language"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                elements = self.shell_elements(response)
                select = next(attrs for tag, attrs in elements if tag == "select" and attrs.get("id") == "languageSwitcher")
                options = [attrs for tag, attrs in elements if tag == "option"]
                self.assertEqual(select["aria-label"], label)
                self.assertEqual({option["value"] for option in options}, {"pt-br", "es", "en"})
                self.assertEqual([option["value"] for option in options if "selected" in option], [selected_value])

    def test_javascript_de_idioma_preserva_path_query_hash_e_origem(self):
        javascript = self.static_source("praticas/js/shell-global.js")
        self.assertIn('new Set(["pt-br", "es", "en"])', javascript)
        self.assertIn("currentUrl.pathname", javascript)
        self.assertIn("currentUrl.search", javascript)
        self.assertIn("currentUrl.hash", javascript)
        self.assertIn('replace(/^\\/(?:es|en)(?=\\/|$)/, "")', javascript)
        self.assertIn('localizedPath.replace(/^\\/+/, "")', javascript)
        self.assertIn("new URL(localizedPath + currentUrl.search + currentUrl.hash, currentUrl.origin)", javascript)
        self.assertIn("destination.origin !== currentUrl.origin", javascript)
        self.assertIn("window.location.assign(destination.href)", javascript)
        self.assertNotIn("window.location.href =", javascript)

    def test_controle_de_contraste_tem_estado_e_rotulos_trilingues(self):
        cases = [
            ("/", "Ativar alto contraste", "Desativar alto contraste"),
            ("/es/", "Activar alto contraste", "Desactivar alto contraste"),
            ("/en/", "Enable high contrast", "Disable high contrast"),
        ]
        for path, enable, disable in cases:
            with self.subTest(path=path):
                elements = self.shell_elements(self.client.get(path))
                button = next(attrs for tag, attrs in elements if tag == "button" and attrs.get("id") == "highContrastToggle")
                self.assertEqual(button["aria-pressed"], "false")
                self.assertEqual(button["aria-label"], enable)
                self.assertEqual(button["data-label-enable"], enable)
                self.assertEqual(button["data-label-disable"], disable)

    def test_preferencia_de_contraste_usa_storage_seguro_e_antecipado(self):
        template = self.source("templates/praticas/base.html")
        javascript = self.static_source("praticas/js/shell-global.js")
        self.assertIn('localStorage.getItem("pjc:ui:high-contrast:v1") === "true"', template)
        self.assertLess(template.index("localStorage.getItem"), template.index("bootstrap.min.css"))
        self.assertIn('const contrastStorageKey = "pjc:ui:high-contrast:v1"', javascript)
        self.assertIn("window.localStorage.getItem", javascript)
        self.assertIn("window.localStorage.setItem", javascript)
        self.assertGreaterEqual(javascript.count("try {"), 2)
        self.assertIn('String(enabled)', javascript)
        self.assertNotIn("username", javascript.lower())

    def test_shell_tem_contratos_de_teclado_foco_e_menu_movel(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        shell = self.shell_html(response)
        javascript = self.static_source("praticas/js/shell-global.js")
        self.assertIn('class="skip-link" href="#conteudo-principal"', html)
        self.assertIn('id="conteudo-principal" tabindex="-1"', html)
        self.assertIn('aria-controls="menuPrincipal" aria-expanded="false"', shell)
        self.assertIn('data-bs-toggle="dropdown" aria-expanded="false"', shell)
        self.assertIn('event.key === "Escape"', javascript)
        self.assertIn('document.addEventListener("keydown"', javascript)
        self.assertNotIn('menu.addEventListener("keydown"', javascript)
        self.assertIn('event.target.closest("a[href]")', javascript)
        self.assertIn("!menu.contains(event.target)", javascript)
        self.assertIn('menu.dataset.initialized === "true"', javascript)
        self.assertIn('toggler.focus()', javascript)

    def test_tokens_reduced_motion_alvos_e_largura_do_shell(self):
        design = self.static_source("praticas/css/design-system.css")
        shell = self.static_source("praticas/css/shell.css")
        for token in ("#432054", "#698d8b", "#4f706e", "#a999bf"):
            self.assertIn(token, design)
        self.assertIn('font-family: "Raleway", "Segoe UI", Arial, sans-serif;', design)
        self.assertIn("--maxw: 1200px;", design)
        self.assertIn("min-height: 44px;", design)
        self.assertIn("@media (max-width: 991.98px)", shell)
        self.assertIn("@media (max-width: 359.98px)", shell)
        self.assertIn("@media (prefers-reduced-motion: reduce)", design)
        self.assertIn(".topline {\n    display: none;", shell)
        self.assertIn(".navbar-institutional {", shell)
        self.assertIn("padding: 0;", shell)

    def test_raleway_local_e_licenca_sao_referenciadas(self):
        design = self.static_source("praticas/css/design-system.css")
        self.assertIn("@font-face", design)
        self.assertIn("font-weight: 300 800;", design)
        self.assertIn("font-style: italic;", design)
        self.assertIn("raleway-v37-latin-normal.woff2", design)
        self.assertIn("raleway-v37-latin-italic.woff2", design)
        for static_path in (
            "praticas/fonts/raleway-v37-latin-normal.woff2",
            "praticas/fonts/raleway-v37-latin-italic.woff2",
            "praticas/fonts/OFL.txt",
        ):
            with self.subTest(static_path=static_path):
                self.assertIsNotNone(finders.find(static_path))

    def test_rodape_usa_asset_local_e_metadados_trilingues(self):
        self.assertIsNotNone(finders.find("praticas/img/barra-de-logos.svg"))
        cases = [
            ("/", "Cooperação Alemã, GIZ, AdaptaInfra, OLACEFS, COMTEMA e CGID"),
            ("/es/", "Cooperación Alemana, GIZ, AdaptaInfra, OLACEFS, COMTEMA y CGID"),
            ("/en/", "German Cooperation, GIZ, AdaptaInfra, OLACEFS, COMTEMA and CGID"),
        ]
        for path, alt in cases:
            with self.subTest(path=path):
                response = self.client.get(path)
                html = unescape(response.content.decode("utf-8"))
                self.assertRegex(html, r'/static/praticas/img/barra-de-logos(?:\.[0-9a-f]+)?\.svg')
                self.assertIn(f'alt="{alt}"', html)
                self.assertNotRegex(html, r'<img[^>]+src=["\']https?://')

    def test_shell_nao_introduz_host_externo_ou_destino_falso(self):
        template = self.source("templates/praticas/base.html")
        javascript = self.static_source("praticas/js/shell-global.js")
        external_urls = re.findall(r"https://[^\"'\s<]+", template)
        self.assertEqual(
            external_urls,
            [
                "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
                "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
            ],
        )
        self.assertEqual({urlparse(url).hostname for url in external_urls}, {"cdn.jsdelivr.net"})
        shell = self.shell_html(self.client.get(reverse("pagina_inicial")))
        self.assertNotIn('href="#"', shell)
        self.assertNotIn("javascript:", shell.lower())
        self.assertNotIn("innerHTML", javascript)
        self.assertNotIn("eval(", javascript)
        self.assertNotIn("fetch(", javascript)

    def test_shell_nao_regrede_autorizacao_existente(self):
        for url_name in ("adicionar_boa_pratica", "meus_envios", "status_envio"):
            with self.subTest(anonymous=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login_usuario"), response["Location"])

        self.client.force_login(self.usuario)
        for url_name in ("painel_revisao", "painel_revisao_edicoes"):
            with self.subTest(ordinary=url_name):
                self.assertEqual(self.client.get(reverse(url_name)).status_code, 302)

        self.client.force_login(self.staff)
        for url_name in ("painel_revisao", "painel_revisao_edicoes"):
            with self.subTest(staff=url_name):
                self.assertEqual(self.client.get(reverse(url_name)).status_code, 200)
