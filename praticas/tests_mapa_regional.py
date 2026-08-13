import json
import re
from pathlib import Path
from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .forms import ExperienciaSubmissaoForm
from .models import EFS, Experiencia, NormaInternacional, Pais, Setor, TipoExperiencia
from .views import MAPA_REGIONAL_ISO3_PARA_GEO_ID, _payload_mapa_regional


class MapaRegionalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.autor = get_user_model().objects.create_user(
            username="autor-mapa",
            email="privado@example.org",
            password="SenhaForte123!",
        )
        cls.brasil = Pais.objects.create(
            nome="Brasil",
            nome_es="Brasil",
            nome_en="Brazil",
            sigla="BRA",
        )
        cls.argentina = Pais.objects.create(
            nome="Argentina",
            nome_es="Argentina",
            nome_en="Argentina",
            sigla="ARG",
        )
        cls.chile = Pais.objects.create(
            nome="Chile",
            nome_es="Chile",
            nome_en="Chile",
            sigla="CHL",
        )
        cls.sem_correspondencia = Pais.objects.create(
            nome="Fora da região",
            nome_es="Fuera de la región",
            nome_en="Outside the region",
            sigla="ZZZ",
        )
        cls.efs_brasil = EFS.objects.create(
            nome="Tribunal de Contas do Brasil",
            nome_es="Tribunal de Cuentas de Brasil",
            nome_en="Brazilian Court of Audit",
            sigla="TCB",
            pais=cls.brasil,
        )
        cls.efs_argentina = EFS.objects.create(
            nome="Auditoria da Argentina",
            nome_es="Auditoría de Argentina",
            nome_en="Audit Office of Argentina",
            sigla="AGA",
            pais=cls.argentina,
        )
        cls.efs_chile = EFS.objects.create(
            nome="Controladoria do Chile",
            nome_es="Contraloría de Chile",
            nome_en="Comptroller of Chile",
            sigla="CCH",
            pais=cls.chile,
        )
        EFS.objects.create(
            nome="Entidade fora da região",
            sigla="EFR",
            pais=cls.sem_correspondencia,
        )
        cls.tipo = TipoExperiencia.objects.create(
            nome="Auditoria",
            nome_es="Auditoría",
            nome_en="Audit",
        )
        cls.setor = Setor.objects.create(
            nome="Energia",
            nome_es="Energía",
            nome_en="Energy",
        )
        cls.norma_publica = NormaInternacional.objects.create(
            nome="Marco público",
            nome_es="Marco público",
            nome_en="Public framework",
        )
        cls.norma_privada = NormaInternacional.objects.create(
            nome="Marco ligado apenas a rascunho",
            nome_es="Marco vinculado solo a borrador",
            nome_en="Draft-only framework",
        )
        cls.publicada_brasil = cls._criar_experiencia(
            "Experiência pública brasileira",
            cls.efs_brasil,
            cls.brasil,
            Experiencia.StatusPublicacao.PUBLICADO,
        )
        cls.publicada_brasil.normas_internacionais.add(cls.norma_publica)
        cls.publicada_argentina = cls._criar_experiencia(
            "Experiência pública argentina",
            cls.efs_argentina,
            cls.argentina,
            Experiencia.StatusPublicacao.PUBLICADO,
        )
        cls.publicada_argentina.normas_internacionais.add(cls.norma_publica)
        cls.rascunho = cls._criar_experiencia(
            "Rascunho confidencial",
            cls.efs_brasil,
            cls.brasil,
            Experiencia.StatusPublicacao.RASCUNHO,
        )
        cls.rascunho.email_contato = "contato-secreto@example.org"
        cls.rascunho.comentario_revisor = "Comentário interno secreto"
        cls.rascunho.save(update_fields=["email_contato", "comentario_revisor"])
        cls.rascunho.normas_internacionais.add(cls.norma_privada)

    @classmethod
    def _criar_experiencia(cls, titulo, efs, pais, status):
        return Experiencia.objects.create(
            autor=cls.autor,
            titulo=titulo,
            titulo_es=titulo,
            titulo_en=titulo,
            efs=efs,
            pais=pais,
            tipo_experiencia=cls.tipo,
            setor=cls.setor,
            ano_execucao=2026,
            descricao="Descrição institucional.",
            status_publicacao=status,
        )

    def _payload(self, caminho="/"):
        response = self.client.get(caminho)
        self.assertEqual(response.status_code, 200)
        return response, response.context["mapa_regional"]

    def test_home_trilingue_exibe_mapa_funcional_e_remove_estado_futuro(self):
        casos = (
            (
                "/",
                "Mapa interativo",
                "EFS da Am&eacute;rica Latina e Caribe",
                "Auditoria coordenada",
                "Selecione uma auditoria coordenada",
            ),
            (
                "/es/",
                "Mapa interactivo",
                "EFS de Am&eacute;rica Latina y el Caribe",
                "Auditor&iacute;a coordinada",
                "Seleccione una auditor&iacute;a coordinada",
            ),
            (
                "/en/",
                "Interactive map",
                "SAIs of Latin America and the Caribbean",
                "Coordinated audit",
                "Select a coordinated audit",
            ),
        )
        for caminho, eyebrow, titulo, rotulo, opcao in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, eyebrow)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, rotulo, html=False)
                self.assertContains(response, opcao, html=False)
                self.assertNotContains(response, "Etapa futura")
                self.assertNotContains(response, "Future stage")

    def test_payload_publico_tem_campos_minimos_e_nenhum_dado_pessoal(self):
        response, payload = self._payload()
        self.assertEqual(
            set(payload),
            {
                "paises",
                "geo_ids_regiao",
                "auditorias_coordenadas",
            },
        )
        self.assertEqual(payload["auditorias_coordenadas"], [])
        campos_pais = {
            "id",
            "sigla",
            "nome",
            "geo_id",
            "efs",
            "experiencias_publicadas",
            "criterios_normativos",
            "criterios_normativos_ids",
            "url_boas_praticas",
            "url_marcos_normativos",
        }
        for pais in payload["paises"]:
            self.assertEqual(set(pais), campos_pais)
            for efs in pais["efs"]:
                self.assertEqual(set(efs), {"nome", "sigla"})

        serialized = json.dumps(payload, ensure_ascii=False)
        html = response.content.decode("utf-8")
        for segredo in (
            "privado@example.org",
            "contato-secreto@example.org",
            "Comentário interno secreto",
            "Rascunho confidencial",
        ):
            self.assertNotIn(segredo, serialized)
            self.assertNotIn(segredo, html)

    def test_norma_compartilhada_usa_uniao_distinta_e_ignora_rascunhos(self):
        _, payload = self._payload()
        por_sigla = {pais["sigla"]: pais for pais in payload["paises"]}
        self.assertEqual(por_sigla["BRA"]["experiencias_publicadas"], 1)
        self.assertEqual(por_sigla["BRA"]["criterios_normativos"], 1)
        self.assertEqual(por_sigla["ARG"]["experiencias_publicadas"], 1)
        self.assertEqual(por_sigla["ARG"]["criterios_normativos"], 1)
        self.assertEqual(por_sigla["CHL"]["experiencias_publicadas"], 0)
        self.assertEqual(por_sigla["CHL"]["criterios_normativos"], 0)

        brasil_ids = por_sigla["BRA"]["criterios_normativos_ids"]
        argentina_ids = por_sigla["ARG"]["criterios_normativos_ids"]
        chile_ids = por_sigla["CHL"]["criterios_normativos_ids"]
        self.assertEqual(brasil_ids, [self.norma_publica.pk])
        self.assertEqual(argentina_ids, [self.norma_publica.pk])
        self.assertEqual(len(set(brasil_ids + argentina_ids)), 1)
        self.assertEqual(chile_ids, [])
        self.assertNotIn(
            self.norma_privada.pk,
            brasil_ids + argentina_ids + chile_ids,
        )
        for ids_normativos in (brasil_ids, argentina_ids, chile_ids):
            self.assertEqual(len(ids_normativos), len(set(ids_normativos)))
        self.assertNotIn("ZZZ", por_sigla)

    def test_payload_e_montado_sem_consulta_por_pais(self):
        with self.assertNumQueries(4):
            payload = _payload_mapa_regional()
        self.assertEqual(len(payload["paises"]), 3)

    def test_payload_associa_efs_correta_e_traduz_nomes(self):
        _, payload_pt = self._payload()
        brasil_pt = next(p for p in payload_pt["paises"] if p["sigla"] == "BRA")
        self.assertEqual(brasil_pt["efs"], [{"nome": "Tribunal de Contas do Brasil", "sigla": "TCB"}])

        _, payload_en = self._payload("/en/")
        brasil_en = next(p for p in payload_en["paises"] if p["sigla"] == "BRA")
        self.assertEqual(brasil_en["nome"], "Brazil")
        self.assertEqual(brasil_en["efs"][0]["nome"], "Brazilian Court of Audit")

    def test_urls_individuais_preservam_idioma_e_parametro_real(self):
        _, payload = self._payload("/es/")
        brasil = next(p for p in payload["paises"] if p["sigla"] == "BRA")
        self.assertEqual(
            brasil["url_boas_praticas"],
            f"/es/catalogo/?pais={self.brasil.pk}",
        )
        self.assertEqual(
            brasil["url_marcos_normativos"],
            f"/es/normas-internacionais/?pais={self.brasil.pk}",
        )

    def test_parametros_repetidos_filtram_catalogos_e_pais_sem_publicacao(self):
        consulta = urlencode(
            [("pais", self.brasil.pk), ("pais", self.argentina.pk)]
        )
        response = self.client.get(f"{reverse('catalogo_experiencias')}?{consulta}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_resultados"], 2)

        response = self.client.get(
            reverse("catalogo_experiencias"), {"pais": self.chile.pk}
        )
        self.assertEqual(response.context["total_resultados"], 0)
        response = self.client.get(
            reverse("normas_internacionais"), {"pais": self.chile.pk}
        )
        self.assertEqual(response.context["total_resultados"], 0)

    def test_pais_inexistente_na_url_nao_causa_erro(self):
        for route in ("catalogo_experiencias", "normas_internacionais"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route), {"pais": "999999"})
                self.assertEqual(response.status_code, 200)

    def test_fallback_textual_e_controles_acessiveis_estao_presentes(self):
        response, _ = self._payload()
        self.assertContains(response, "Lista acess&iacute;vel de pa&iacute;ses", html=False)
        self.assertContains(response, 'id="regionalMapForm" method="get"')
        self.assertContains(response, 'name="pais"', count=3)
        self.assertContains(response, 'id="regionalMapCount"')
        self.assertContains(response, 'aria-live="polite"')
        self.assertContains(response, 'id="regionalMapCoordinatedAudit"')
        self.assertContains(response, 'aria-describedby="regionalMapCoordinatedStatus"')
        self.assertContains(response, 'id="regionalMapCoordinatedStatus"')
        self.assertContains(response, 'id="regionalMapCoordinatedAudit"', html=False)
        self.assertContains(response, "disabled")
        self.assertContains(response, '<noscript>')
        self.assertContains(response, 'formaction="/catalogo/"')
        self.assertContains(response, 'formaction="/normas-internacionais/"')
        self.assertContains(
            response,
            '<button class="home-map-clear" id="regionalMapClear" type="reset">',
            html=False,
        )

    def test_selecao_manual_e_individual_e_textos_nao_indicam_multisselecao(self):
        casos = (
            ("/", "Selecione um pa&iacute;s no mapa", "Selecione um pa&iacute;s"),
            ("/es/", "Selecciona un pa&iacute;s en el mapa", "Selecciona un pa&iacute;s"),
            ("/en/", "Select one country on the map", "Select one country"),
        )
        textos_multisselecao = (
            "vários ao mesmo tempo",
            "varios a la vez",
            "several at once",
            "um ou mais países",
            "uno o más países",
            "one or more countries",
        )

        for caminho, instrucao, legenda in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                html = response.content.decode("utf-8")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, instrucao, html=False)
                self.assertContains(response, legenda, html=False)
                for texto in textos_multisselecao:
                    self.assertNotIn(texto, html)

                inputs = re.findall(
                    r"<input\s+[^>]*name=\"pais\"[^>]*>",
                    html,
                )
                self.assertGreater(len(inputs), 1)
                for country_input in inputs:
                    self.assertIn('type="radio"', country_input)
                    self.assertNotIn('type="checkbox"', country_input)

                form = html.split('id="regionalMapForm"', 1)[1].split(
                    "</form>", 1
                )[0]
                self.assertNotRegex(
                    form,
                    r'type="checkbox"[^>]*name="pais"',
                )

        script = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )
        self.assertIn("const countryRadios", script)
        self.assertIn("radio.checked = selectedIds.has(radio.value);", script)
        self.assertIn("selectedIds.clear();", script)
        self.assertNotIn("countryCheckboxes", script)

    def test_nomenclatura_publica_de_entidades_associadas_e_trilingue(self):
        casos = (
            ("/", "Entidades associadas", "Entidades associadas ao pa&iacute;s selecionado"),
            ("/es/", "Entidades asociadas", "Entidades asociadas al pa&iacute;s seleccionado"),
            ("/en/", "Associated entities", "Entities associated with the selected country"),
        )

        for caminho, titulo, aria_label in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, f'aria-label="{aria_label}"', html=False)

    def test_select_coordenado_permanece_independente_responsivo_e_sem_dados_ficticios(self):
        response, payload = self._payload()
        css = Path(finders.find("praticas/css/home.css")).read_text(
            encoding="utf-8"
        )

        self.assertEqual(payload["auditorias_coordenadas"], [])
        self.assertContains(response, 'id="regionalMapCoordinatedAudit"')
        self.assertContains(response, "disabled")
        self.assertContains(
            response,
            "N&atilde;o h&aacute; auditorias coordenadas com EFS participantes adicionais dispon&iacute;veis.",
            html=False,
        )
        self.assertRegex(
            css,
            r"\.home-map-coordinated-control select\s*\{[^}]*width: 100%[^}]*"
            r"max-width: 100%[^}]*min-height: 48px[^}]*"
            r"padding: 10px 42px 10px 12px[^}]*overflow: hidden",
        )

        script = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )
        funcao = script.split("function updateCoordinatedHighlight", 1)[1].split(
            "function showTooltip", 1
        )[0]
        self.assertNotIn("selectedIds", funcao)
        self.assertNotIn("countryRadios", funcao)

    def test_assets_sao_locais_e_javascript_e_progressivo(self):
        arquivos = (
            "praticas/js/mapa-regional.js",
            "praticas/vendor/d3/d3-7.9.0.min.js",
            "praticas/vendor/topojson/topojson-client-3.1.0.min.js",
            "praticas/data/countries-50m.json",
            "praticas/vendor/THIRD_PARTY_NOTICES.md",
        )
        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo):
                self.assertIsNotNone(finders.find(arquivo))

        response, _ = self._payload()
        html = response.content.decode("utf-8")
        self.assertIn("/static/praticas/vendor/d3/d3-7.9.0.min.", html)
        self.assertIn("/static/praticas/data/countries-50m.", html)
        self.assertNotIn("d3js.org", html)
        self.assertNotIn("unpkg.com", html)

        script = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )
        self.assertIn('event.key === "Enter"', script)
        self.assertIn('event.key === " "', script)
        self.assertIn('attr("aria-pressed"', script)
        self.assertIn("showLoadError", script)
        self.assertIn("const normativeIds = new Set();", script)
        self.assertIn("country.criterios_normativos_ids", script)
        self.assertIn('form.addEventListener("reset"', script)
        self.assertIn("selectedIds.clear();", script)
        self.assertIn("const coordinatedHighlightedIds = new Set();", script)
        self.assertIn('.classed("is-coordinated"', script)
        self.assertIn('coordinatedSelect.addEventListener("change"', script)
        self.assertNotIn('clearButton.addEventListener("click"', script)
        self.assertNotIn("totalNorms +=", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("geolocation", script)
        self.assertNotIn("https://", script)

    def test_aruba_e_curacao_preservam_geo_ids_e_payload_institucional(self):
        aruba = Pais.objects.create(
            nome="Aruba",
            nome_es="Aruba",
            nome_en="Aruba",
            sigla="ABW",
        )
        curacao = Pais.objects.create(
            nome="Curaçao",
            nome_es="Curazao",
            nome_en="Curaçao",
            sigla="CUW",
        )
        EFS.objects.create(nome="EFS Aruba", sigla="EFA", pais=aruba)
        EFS.objects.create(nome="EFS Curaçao", sigla="EFC", pais=curacao)

        payload = _payload_mapa_regional()
        por_sigla = {pais["sigla"]: pais for pais in payload["paises"]}

        self.assertEqual(MAPA_REGIONAL_ISO3_PARA_GEO_ID["ABW"], "533")
        self.assertEqual(MAPA_REGIONAL_ISO3_PARA_GEO_ID["CUW"], "531")
        self.assertEqual(por_sigla["ABW"]["geo_id"], "533")
        self.assertEqual(por_sigla["CUW"]["geo_id"], "531")

    def test_auditoria_coordenada_publicada_une_e_deduplica_paises(self):
        efs_argentina_adicional = EFS.objects.create(
            nome="Segunda EFS Argentina",
            sigla="A2",
            pais=self.argentina,
        )
        self.publicada_brasil.efs_participantes.add(
            self.efs_argentina,
            efs_argentina_adicional,
            self.efs_chile,
        )

        payload = _payload_mapa_regional()
        self.assertEqual(len(payload["auditorias_coordenadas"]), 1)
        auditoria = payload["auditorias_coordenadas"][0]

        self.assertEqual(auditoria["id"], self.publicada_brasil.pk)
        self.assertEqual(
            auditoria["efs_lider"],
            {
                "id": self.efs_brasil.pk,
                "nome": "Tribunal de Contas do Brasil",
                "sigla": "TCB",
            },
        )
        self.assertEqual(
            [pais["id"] for pais in auditoria["paises"]],
            [self.argentina.pk, self.brasil.pk, self.chile.pk],
        )
        self.assertEqual(
            len({pais["id"] for pais in auditoria["paises"]}),
            3,
        )
        self.assertEqual(self.publicada_brasil.efs_participantes.count(), 3)

    def test_payload_coordenado_exclui_rascunhos_e_experiencias_sem_participantes(self):
        self.rascunho.efs_participantes.add(self.efs_argentina)
        self.publicada_argentina.efs_participantes.add(self.efs_argentina)

        payload = _payload_mapa_regional()
        ids = {auditoria["id"] for auditoria in payload["auditorias_coordenadas"]}

        self.assertNotIn(self.rascunho.pk, ids)
        self.assertNotIn(self.publicada_brasil.pk, ids)
        self.assertNotIn(self.publicada_argentina.pk, ids)
        self.assertFalse(self.publicada_brasil.efs_participantes.exists())
        self.assertQuerySetEqual(
            self.publicada_argentina.efs_participantes.all(),
            [self.efs_argentina],
        )

    def test_payload_coordenado_respeita_idioma_atual(self):
        self.publicada_brasil.titulo = "Auditoria coordenada PT"
        self.publicada_brasil.titulo_es = "Auditoría coordinada ES"
        self.publicada_brasil.titulo_en = "Coordinated audit EN"
        self.publicada_brasil.save(
            update_fields=["titulo", "titulo_es", "titulo_en"]
        )
        self.publicada_brasil.efs_participantes.add(self.efs_argentina)

        casos = (
            ("/", "Auditoria coordenada PT"),
            ("/es/", "Auditoría coordinada ES"),
            ("/en/", "Coordinated audit EN"),
        )
        for caminho, titulo in casos:
            with self.subTest(caminho=caminho):
                _, payload = self._payload(caminho)
                self.assertEqual(
                    payload["auditorias_coordenadas"][0]["titulo"],
                    titulo,
                )

    def test_many_to_many_e_curadoria_admin_sem_expor_formulario_publico(self):
        self.publicada_brasil.efs_participantes.add(
            self.efs_argentina,
            self.efs_chile,
        )

        self.assertQuerySetEqual(
            self.publicada_brasil.efs_participantes.order_by("pk"),
            [self.efs_argentina, self.efs_chile],
        )
        experiencia_admin = admin.site._registry[Experiencia]
        self.assertIn("efs_participantes", experiencia_admin.filter_horizontal)
        self.assertNotIn("efs_participantes", ExperienciaSubmissaoForm().fields)

    def test_destaque_coordenado_nao_altera_selecao_manual(self):
        script = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )
        funcao = script.split(
            "function updateCoordinatedHighlight", 1
        )[1].split("function showTooltip", 1)[0]

        self.assertIn("coordinatedHighlightedIds.clear();", funcao)
        self.assertIn("coordinatedHighlightedIds.add", funcao)
        self.assertNotIn("selectedIds", funcao)
        self.assertNotIn("countryRadios", funcao)
        self.assertNotIn("form.submit", funcao)
        self.assertNotIn("window.location", funcao)

    def test_microterritorios_usam_centroid_hit_target_e_controle_acessivel(self):
        script = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )

        self.assertIn('new Set(["531", "533"])', script)
        self.assertIn("path.centroid(feature)", script)
        self.assertIn('attr("class", "home-map-microterritory-hit")', script)
        self.assertIn('attr("r", 16)', script)
        self.assertIn("bindCountryControl(microterritoryControls)", script)
        self.assertIn('.append("title")', script)

    def test_ids_geograficos_configurados_existem_no_world_atlas_local(self):
        caminho = Path(finders.find("praticas/data/countries-50m.json"))
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        ids_disponiveis = {
            str(geometria["id"]).zfill(3)
            for geometria in dados["objects"]["countries"]["geometries"]
            if geometria.get("id") is not None
        }
        ids_configurados = {
            str(geo_id).zfill(3)
            for geo_id in MAPA_REGIONAL_ISO3_PARA_GEO_ID.values()
        }
        ids_ausentes = sorted(ids_configurados - ids_disponiveis)

        self.assertFalse(
            ids_ausentes,
            "IDs geográficos configurados ausentes em countries-50m.json: "
            + ", ".join(ids_ausentes),
        )

    def test_requisicao_da_home_nao_modifica_dados(self):
        contagens_antes = (
            Pais.objects.count(),
            EFS.objects.count(),
            Experiencia.objects.count(),
            NormaInternacional.objects.count(),
        )
        self.client.get(reverse("pagina_inicial"))
        self.assertEqual(
            contagens_antes,
            (
                Pais.objects.count(),
                EFS.objects.count(),
                Experiencia.objects.count(),
                NormaInternacional.objects.count(),
            ),
        )
