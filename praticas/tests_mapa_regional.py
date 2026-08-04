import json
from pathlib import Path
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .models import EFS, Experiencia, NormaInternacional, Pais, Setor, TipoExperiencia
from .views import _payload_mapa_regional


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
            ("/", "Mapa interativo", "EFS da Am&eacute;rica Latina e Caribe"),
            ("/es/", "Mapa interactivo", "EFS de Am&eacute;rica Latina y el Caribe"),
            ("/en/", "Interactive map", "SAIs of Latin America and the Caribbean"),
        )
        for caminho, eyebrow, titulo in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, eyebrow)
                self.assertContains(response, titulo, html=False)
                self.assertNotContains(response, "Etapa futura")
                self.assertNotContains(response, "Future stage")

    def test_payload_publico_tem_campos_minimos_e_nenhum_dado_pessoal(self):
        response, payload = self._payload()
        self.assertEqual(
            set(payload),
            {
                "paises",
                "geo_ids_regiao",
            },
        )
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
        with self.assertNumQueries(3):
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
        self.assertContains(response, 'name="pais"', count=3)
        self.assertContains(response, 'id="regionalMapCount"')
        self.assertContains(response, 'aria-live="polite"')
        self.assertContains(response, '<noscript>')
        self.assertContains(response, 'formaction="/catalogo/"')
        self.assertContains(response, 'formaction="/normas-internacionais/"')

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
        self.assertNotIn("totalNorms +=", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("geolocation", script)
        self.assertNotIn("https://", script)

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

    def test_fase_nao_cria_migration_posterior_a_0012(self):
        migration_dir = Path(__file__).resolve().parent / "migrations"
        numeradas = sorted(
            path.name
            for path in migration_dir.glob("[0-9][0-9][0-9][0-9]_*.py")
        )
        self.assertTrue(numeradas)
        self.assertTrue(numeradas[-1].startswith("0012_"))
