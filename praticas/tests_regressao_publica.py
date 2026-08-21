import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import (
    DimensaoJusticaClimatica,
    EFS,
    EixoGuia,
    Experiencia,
    Ferramenta,
    GrupoVulneravel,
    NormaInternacional,
    NormaInternacionalPais,
    Pais,
    Setor,
    TipoExperiencia,
    VersaoGuia,
)
from .views import MAPA_REGIONAL_ISO3_PARA_GEO_ID, _payload_mapa_regional


class InventarioDOM(HTMLParser):
    ELEMENTOS_VAZIOS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    TAGS_ESTRUTURAIS = {
        "article",
        "button",
        "dialog",
        "form",
        "input",
        "nav",
        "section",
        "select",
        "video",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.classes = Counter()
        self.tags = Counter()
        self.links = []
        self.opcoes_idioma = []
        self.botoes_desabilitados = []
        self.controles = []
        self._pilha_contexto = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        dentro_seletor_idioma = atributos.get("id") == "languageSwitcher" or any(
            contexto[1] for contexto in self._pilha_contexto
        )
        if tag in self.TAGS_ESTRUTURAIS:
            self.tags[tag] += 1
        if atributos.get("id"):
            self.ids.append(atributos["id"])
        for classe in atributos.get("class", "").split():
            self.classes[classe] += 1
        if tag == "a":
            self.links.append((atributos.get("href"), dentro_seletor_idioma))
        if tag == "option" and dentro_seletor_idioma:
            self.opcoes_idioma.append(atributos.get("value"))
        if tag == "button":
            self.botoes_desabilitados.append("disabled" in atributos)
        if tag in {"input", "select", "textarea"}:
            self.controles.append(
                (tag, atributos.get("type", ""), atributos.get("name", ""))
            )
        if tag not in self.ELEMENTOS_VAZIOS:
            self._pilha_contexto.append((tag, dentro_seletor_idioma))

    def handle_endtag(self, tag):
        for indice in range(len(self._pilha_contexto) - 1, -1, -1):
            if self._pilha_contexto[indice][0] == tag:
                del self._pilha_contexto[indice:]
                break


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class RegressaoPublicaTests(TestCase):
    ROTAS_PUBLICAS = (
        "/",
        "/exemplos-injustica-climatica/",
        "/catalogo/",
        "/normas-internacionais/",
        "/ferramentas/",
        "/banco-tecnico/",
        "/sobre/",
        "/entrar/",
        "/cadastro/",
    )
    PREFIXOS = ("", "/es", "/en")

    @classmethod
    def setUpTestData(cls):
        usuario_model = get_user_model()
        cls.usuario = usuario_model.objects.create_user(
            "usuario-regressao", password="senha-regressao"
        )
        cls.staff = usuario_model.objects.create_user(
            "staff-regressao", password="senha-regressao", is_staff=True
        )
        cls.brasil = Pais.objects.create(
            nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA"
        )
        cls.aruba = Pais.objects.create(
            nome="Aruba", nome_es="Aruba", nome_en="Aruba", sigla="ABW"
        )
        cls.curacao = Pais.objects.create(
            nome="Curaçao", nome_es="Curazao", nome_en="Curaçao", sigla="CUW"
        )
        cls.efs_brasil = EFS.objects.create(
            nome="Entidade associada Brasil",
            nome_es="Entidad asociada Brasil",
            nome_en="Brazil associated entity",
            sigla="EAB",
            pais=cls.brasil,
        )
        EFS.objects.create(nome="EFS Aruba", sigla="EFA", pais=cls.aruba)
        cls.efs_curacao = EFS.objects.create(
            nome="SOAB Curaçao", sigla="SOAB", pais=cls.curacao
        )
        cls.tipo = TipoExperiencia.objects.create(
            nome="Auditoria", nome_es="Auditoría", nome_en="Audit"
        )
        cls.setor = Setor.objects.create(
            nome="Energia", nome_es="Energía", nome_en="Energy"
        )
        cls.dimensao = DimensaoJusticaClimatica.objects.create(
            nome="Equidade", nome_es="Equidad", nome_en="Equity"
        )
        cls.grupo = GrupoVulneravel.objects.create(
            nome="Comunidades locais",
            nome_es="Comunidades locales",
            nome_en="Local communities",
        )
        cls.norma_com_links = NormaInternacional.objects.create(
            nome="Marco verificável",
            nome_es="Marco verificable",
            nome_en="Verifiable framework",
            resumo_es="Descripción institucional en español.",
            ano=2024,
            ano_texto="2024",
            natureza_juridica="Vinculante",
            setores_aplicaveis="Energía",
            url_referencia="https://example.org/fonte",
            ficha_tecnica_url="https://example.org/ficha",
        )
        cls.norma_sem_links = NormaInternacional.objects.create(
            nome="Marco sem links",
            nome_es="Marco sin enlaces",
            nome_en="Framework without links",
            resumo_es="Segunda descripción institucional.",
            natureza_juridica="No vinculante",
            setores_aplicaveis="Energía",
        )
        NormaInternacionalPais.objects.create(
            norma=cls.norma_com_links,
            pais=cls.brasil,
            status="Ratificado",
        )
        cls.pratica = cls._criar_pratica(
            "Prática pública",
            cls.efs_brasil,
            cls.brasil,
            contato="Contato Final",
        )
        cls.pratica.dimensoes_consideradas.add(cls.dimensao)
        cls.pratica.grupos_vulneraveis.add(cls.grupo)
        cls.pratica.normas_internacionais.add(cls.norma_com_links)
        cls.pratica_curacao = cls._criar_pratica(
            "Prática Curaçao", cls.efs_curacao, cls.curacao
        )
        cls.pratica_curacao.normas_internacionais.add(
            cls.norma_com_links,
            cls.norma_sem_links,
        )
        cls.rascunho = cls._criar_pratica(
            "Rascunho não público",
            cls.efs_brasil,
            cls.brasil,
            status=Experiencia.StatusPublicacao.RASCUNHO,
        )
        Ferramenta.objects.create(
            codigo="ferramenta-regressao",
            titulo="Ferramenta pública",
            titulo_es="Herramienta pública",
            titulo_en="Public tool",
            descricao="Descrição da ferramenta.",
            descricao_es="Descripción de la herramienta.",
            descricao_en="Tool description.",
            responsavel="OLACEFS",
            periodo="2026",
            setor=cls.setor,
            url="https://example.org/ferramenta",
            situacao=Ferramenta.Situacao.PUBLICADA,
            ordem=1,
        )
        cls.guia_rascunho = VersaoGuia.objects.create(
            codigo="guia-nao-homologado",
            fonte="fixture/teste.json",
            sha256_fonte="a" * 64,
        )
        EixoGuia.objects.create(
            versao=cls.guia_rascunho,
            codigo="eixo-nao-publico",
            nome_es="Contenido no homologado",
            ordem=1,
        )

    @classmethod
    def _criar_pratica(
        cls, titulo, efs, pais, *, contato="", status=Experiencia.StatusPublicacao.PUBLICADO
    ):
        return Experiencia.objects.create(
            autor=cls.usuario,
            titulo=titulo,
            titulo_es=f"{titulo} ES",
            titulo_en=f"{titulo} EN",
            efs=efs,
            pais=pais,
            tipo_experiencia=cls.tipo,
            setor=cls.setor,
            ano_execucao=2026,
            descricao="Descrição pública.",
            descricao_es="Descripción pública.",
            descricao_en="Public description.",
            pessoa_responsavel=contato,
            email_contato="contato@example.org" if contato else "",
            status_publicacao=status,
        )

    def setUp(self):
        translation.activate("pt-br")
        self.client.cookies.clear()

    def tearDown(self):
        self.client.cookies.clear()
        translation.deactivate_all()

    def _caminho(self, prefixo, rota):
        return f"{prefixo}{rota}" if rota != "/" else f"{prefixo}/"

    def _inventario(self, caminho, client=None):
        response = (client or self.client).get(caminho)
        self.assertEqual(response.status_code, 200, caminho)
        inventario = InventarioDOM()
        inventario.feed(response.content.decode("utf-8"))
        return response, inventario

    def _href_normalizado(self, href):
        if href and href.startswith(("/es/", "/en/")):
            return href[3:]
        return href

    def _assert_prefixo_idioma(self, href, prefixo):
        if not href or not href.startswith("/") or href.startswith("//"):
            return
        if prefixo:
            self.assertTrue(
                href == f"{prefixo}/" or href.startswith(f"{prefixo}/"), href
            )
        else:
            self.assertFalse(href.startswith(("/es/", "/en/")), href)

    def _assert_destino_seletor_idioma(self, href, rota):
        destino = urlsplit(href)
        self.assertEqual(destino.scheme, "", href)
        self.assertEqual(destino.netloc, "", href)
        self.assertIn(
            destino.path,
            {self._caminho(prefixo, rota) for prefixo in self.PREFIXOS},
            href,
        )

    def _assinatura_estrutural(self, inventario):
        classes_criticas = {
            classe: total
            for classe, total in inventario.classes.items()
            if classe.startswith(
                ("home-", "catalog-", "library-", "norm-", "tools-", "guia-", "account-")
            )
        }
        return {
            "ids": inventario.ids,
            "tags": inventario.tags,
            "classes": classes_criticas,
            "hrefs": [
                self._href_normalizado(href)
                for href, link_seletor_idioma in inventario.links
                if not link_seletor_idioma
            ],
            "botoes_desabilitados": inventario.botoes_desabilitados,
            "controles": inventario.controles,
        }

    def test_rotas_publicas_mantem_status_componentes_e_paridade_estrutural(self):
        for rota in self.ROTAS_PUBLICAS:
            with self.subTest(rota=rota):
                assinaturas = []
                for prefixo in self.PREFIXOS:
                    response, inventario = self._inventario(
                        self._caminho(prefixo, rota)
                    )
                    html = response.content.decode("utf-8")
                    self.assertIn('class="navbar ', html)
                    self.assertIn('class="footer-institutional ', html)
                    self.assertIn('id="languageSwitcher"', html)
                    self.assertIn('id="highContrastToggle"', html)
                    self.assertCountEqual(
                        inventario.opcoes_idioma,
                        ["pt-br", "es", "en"],
                    )
                    self.assertEqual(len(inventario.opcoes_idioma), 3)
                    assinaturas.append(self._assinatura_estrutural(inventario))
                self.assertEqual(assinaturas[0], assinaturas[1])
                self.assertEqual(assinaturas[0], assinaturas[2])

    def test_home_preserva_ordem_componentes_e_fundamentos_semanticos(self):
        conceitos = {
            "": ("Equidade e Inclusão", "Participação Social", "Responsabilidades comuns, porém diferenciadas"),
            "/es": ("Equidad e Inclusión", "Participación Social", "Responsabilidades comunes, pero diferenciadas"),
            "/en": ("Equity and Inclusion", "Social Participation", "Common but differentiated responsibilities"),
        }
        position_paper = (
            "https://olacefs.com/giz/wp-content/uploads/sites/14/2025/11/"
            "Position_Paper_Miolo_ESP.pdf"
        )
        for prefixo, titulos in conceitos.items():
            with self.subTest(prefixo=prefixo or "pt-br"):
                response, inventario = self._inventario(self._caminho(prefixo, "/"))
                html = response.content.decode("utf-8")
                posicoes = (
                    html.index('class="jc-hero home-block"'),
                    html.index('id="testimonialsSection"'),
                    html.index('id="pillarsSection"'),
                    html.index('id="mapSection"'),
                    html.index('id="videoSection"'),
                )
                self.assertEqual(posicoes, tuple(sorted(posicoes)))
                self.assertEqual(inventario.classes["home-foundation-tab"], 3)
                self.assertEqual(inventario.classes["home-foundation-strategy"], 3)
                self.assertEqual(inventario.classes["home-foundation-audit-item"], 6)
                conceito = html.split('id="concepto-pane"', 1)[1].split(
                    'id="controle-pane"', 1
                )[0]
                self.assertEqual(conceito.count('class="home-foundation-strategy"'), 3)
                for titulo in titulos:
                    self.assertIn(titulo, conceito)
                self.assertEqual(html.count(f'href="{position_paper}"'), 1)
                self.assertEqual(
                    html.count('class="home-foundation-actions"'), 2
                )
                self.assertIn('id="regionalMap"', html)
                self.assertIn('id="home-video-error" role="status" hidden', html)
                self.assertNotIn("autoplay", html)

    def test_mapa_preserva_paises_microterritorios_e_selecao_unitaria(self):
        payload = _payload_mapa_regional()
        por_sigla = {pais["sigla"]: pais for pais in payload["paises"]}
        institucionais = {
            pais.sigla
            for pais in Pais.objects.filter(
                efs__isnull=False,
                sigla__in=MAPA_REGIONAL_ISO3_PARA_GEO_ID,
            ).distinct()
        }
        self.assertEqual(set(por_sigla), institucionais)
        self.assertEqual(MAPA_REGIONAL_ISO3_PARA_GEO_ID["ABW"], "533")
        self.assertEqual(MAPA_REGIONAL_ISO3_PARA_GEO_ID["CUW"], "531")
        self.assertEqual(por_sigla["ABW"]["geo_id"], "533")
        self.assertEqual(por_sigla["CUW"]["geo_id"], "531")
        self.assertEqual(por_sigla["CUW"]["experiencias_publicadas"], 1)
        self.assertEqual(len(por_sigla["CUW"]["criterios_normativos_ids"]), 2)

        script = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )
        ids_microterritorios = re.search(
            r"const\s+microterritoryGeoIds\s*=\s*new\s+Set\s*\(\s*\[([^]]+)]",
            script,
        )
        self.assertIsNotNone(ids_microterritorios)
        ids_encontrados = re.findall(
            r'["\'](\d{3})["\']', ids_microterritorios.group(1)
        )
        self.assertCountEqual(ids_encontrados, ["531", "533"])
        self.assertEqual(len(ids_encontrados), 2)
        self.assertIn("function projectedFeatureCentroid", script)
        self.assertIn("path.centroid(feature)", script)
        self.assertIn("d3.geoCentroid(feature)", script)
        self.assertIn("Number.isFinite", script)
        self.assertIn("function separatedMicroterritoryPositions", script)
        self.assertIn("institutionalMicroterritoryGeoIds.size", script)
        raio_hit = re.search(
            r'attr\s*\(\s*["\']class["\']\s*,\s*'
            r'["\']home-map-microterritory-hit["\']\s*\)'
            r'.*?attr\s*\(\s*["\']r["\']\s*,\s*(\d+)\s*\)',
            script,
            re.DOTALL,
        )
        raio_marker = re.search(
            r'attr\s*\(\s*["\']class["\']\s*,\s*'
            r'["\']home-map-microterritory-marker["\']\s*\)'
            r'.*?attr\s*\(\s*["\']r["\']\s*,\s*(\d+)\s*\)',
            script,
            re.DOTALL,
        )
        self.assertIsNotNone(raio_hit)
        self.assertIsNotNone(raio_marker)
        hitbox = int(raio_hit.group(1))
        marker = int(raio_marker.group(1))
        self.assertEqual(hitbox, 16)
        self.assertEqual(marker, 8)
        self.assertGreater(hitbox, marker)
        separacao_minima = re.search(
            r"const\s+microterritoryMinimumSeparation\s*=\s*(\d+)", script
        )
        self.assertIsNotNone(separacao_minima)
        self.assertGreater(int(separacao_minima.group(1)), hitbox * 2)
        self.assertIn("Math.hypot", script)
        self.assertIn("positionedMicroterritories", script)
        self.assertIn("item.position[0]", script)
        self.assertIn("item.position[1]", script)
        self.assertIn("selectedIds.clear();", script)
        self.assertIn('form.addEventListener("reset"', script)
        self.assertIn('event.key === "Enter"', script)
        self.assertIn('event.key === " "', script)
        self.assertIn("showTooltip(event, countryForFeature(feature))", script)
        funcao_coordenada = script.split(
            "function updateCoordinatedHighlight", 1
        )[1].split("function showTooltip", 1)[0]
        self.assertNotIn("selectedIds", funcao_coordenada)

        response = self.client.get("/")
        html = response.content.decode("utf-8")
        inputs_pais = [
            trecho.split(">", 1)[0]
            for trecho in html.split("<input")[1:]
            if 'name="pais"' in trecho.split(">", 1)[0]
        ]
        self.assertEqual(len(inputs_pais), len(institucionais))
        self.assertTrue(all('type="radio"' in trecho for trecho in inputs_pais))
        self.assertTrue(all('type="checkbox"' not in trecho for trecho in inputs_pais))
        self.assertIn('id="regionalMapClear" type="reset"', html)
        self.assertIn('formaction="/catalogo/"', html)
        self.assertIn('formaction="/normas-internacionais/"', html)

    def test_catalogos_e_detalhe_preservam_invariantes_de_produto(self):
        for prefixo in self.PREFIXOS:
            with self.subTest(prefixo=prefixo or "pt-br"):
                catalogo, inventario_catalogo = self._inventario(
                    self._caminho(prefixo, "/catalogo/")
                )
                self.assertEqual(inventario_catalogo.classes["catalog-card"], 2)
                self.assertEqual(inventario_catalogo.classes["catalog-filter-group"], 4)
                self.assertNotContains(catalogo, self.rascunho.titulo)

                detalhe, inventario_detalhe = self._inventario(
                    self._caminho(prefixo, f"/experiencias/{self.pratica.pk}/")
                )
                html_detalhe = detalhe.content.decode("utf-8")
                self.assertIn('id="experience-vulnerable-groups"', html_detalhe)
                self.assertIn('id="experience-contact"', html_detalhe)
                self.assertGreater(
                    html_detalhe.index('id="experience-contact"'),
                    html_detalhe.index('id="experience-vulnerable-groups"'),
                )
                self.assertEqual(html_detalhe.count("Contato Final"), 1)
                self.assertNotIn("Pessoa responsável", html_detalhe)
                self.assertGreater(inventario_detalhe.tags["section"], 3)

                normas, inventario_normas = self._inventario(
                    self._caminho(prefixo, "/normas-internacionais/")
                )
                html_normas = normas.content.decode("utf-8")
                self.assertEqual(inventario_normas.classes["library-card"], 2)
                self.assertEqual(inventario_normas.classes["norm-dialog"], 2)
                self.assertIn('name="natureza"', html_normas)
                self.assertIn("Ratificado", html_normas)
                self.assertEqual(html_normas.count('href="https://example.org/fonte"'), 2)
                self.assertEqual(html_normas.count('href="https://example.org/ficha"'), 2)
                self.assertIn('class="library-compendium" type="button" disabled', html_normas)
                self.assertNotIn("download=", html_normas)
                normas_filtradas = self.client.get(
                    self._caminho(prefixo, "/normas-internacionais/"),
                    {"natureza": "Vinculante"},
                )
                self.assertEqual(normas_filtradas.status_code, 200)
                self.assertEqual(normas_filtradas.context["total_resultados"], 1)
                self.assertContains(normas_filtradas, 'value="Vinculante" selected')

                _, inventario_ferramentas = self._inventario(
                    self._caminho(prefixo, "/ferramentas/")
                )
                self.assertEqual(inventario_ferramentas.classes["tools-row"], 1)
                self.assertEqual(inventario_ferramentas.classes["tools-link"], 1)

    def test_guia_publico_fica_oculto_e_preview_permanece_protegida(self):
        rotas_guia = (
            "/guia/",
            "/guia/eixos/",
            "/guia/setores/",
        )
        for prefixo in self.PREFIXOS:
            with self.subTest(prefixo=prefixo or "pt-br"):
                home = self.client.get(self._caminho(prefixo, "/"))
                self.assertEqual(home.status_code, 200)
                self.assertNotContains(home, f'href="{self._caminho(prefixo, "/guia/")}"')
                for rota in rotas_guia:
                    response = self.client.get(self._caminho(prefixo, rota))
                    self.assertEqual(response.status_code, 404)
                preview = self.client.get(
                    self._caminho(prefixo, "/guia/preview/")
                )
                self.assertEqual(preview.status_code, 302)

    def test_autenticacao_e_perfis_preservam_protecao_trilingue(self):
        protegidas_usuario = ("/adicionar-boa-pratica/", "/meus-envios/", "/status-envio/")
        protegidas_staff = ("/painel-revisao/", "/painel-revisao-edicoes/")
        client_usuario = self.client_class()
        client_usuario.force_login(self.usuario)
        client_staff = self.client_class()
        client_staff.force_login(self.staff)

        for prefixo in self.PREFIXOS:
            for rota in protegidas_usuario:
                caminho = self._caminho(prefixo, rota)
                with self.subTest(caminho=caminho, perfil="usuario"):
                    self.assertEqual(self.client.get(caminho).status_code, 302)
                    self.assertEqual(client_usuario.get(caminho).status_code, 200)
            for rota in protegidas_staff:
                caminho = self._caminho(prefixo, rota)
                with self.subTest(caminho=caminho, perfil="staff"):
                    self.assertEqual(client_usuario.get(caminho).status_code, 302)
                    self.assertEqual(client_staff.get(caminho).status_code, 200)

    def test_links_e_ctas_publicos_nao_apontam_para_destinos_invalidos(self):
        hrefs_por_rota = {}
        rotas = self.ROTAS_PUBLICAS + (f"/experiencias/{self.pratica.pk}/",)
        for rota in rotas:
            for prefixo in self.PREFIXOS:
                caminho = self._caminho(prefixo, rota)
                _, inventario = self._inventario(caminho)
                for href, link_seletor_idioma in inventario.links:
                    with self.subTest(caminho=caminho, href=href):
                        self.assertNotIn(href, (None, "", "#"))
                        self.assertNotIn(".local", href)
                        self.assertFalse(href.startswith("file://"))
                        self.assertFalse(href.startswith("["))
                        if href.startswith(("http://", "https://")):
                            parsed = urlsplit(href)
                            self.assertIn(parsed.scheme, {"http", "https"})
                            self.assertTrue(parsed.netloc)
                        if link_seletor_idioma:
                            self._assert_destino_seletor_idioma(href, rota)
                        else:
                            self._assert_prefixo_idioma(href, prefixo)
                hrefs_por_rota[(rota, prefixo)] = [
                    self._href_normalizado(href)
                    for href, link_seletor_idioma in inventario.links
                    if not link_seletor_idioma
                ]

        for rota in rotas:
            self.assertEqual(hrefs_por_rota[(rota, "")], hrefs_por_rota[(rota, "/es")])
            self.assertEqual(hrefs_por_rota[(rota, "")], hrefs_por_rota[(rota, "/en")])
