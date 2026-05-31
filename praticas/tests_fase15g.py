from django.test import TestCase
from django.urls import reverse


class RevisaoVisualPublicaTests(TestCase):
    def test_base_contem_refinamento_visual_publico(self):
        response = self.client.get(reverse("pagina_inicial"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertIn("Fase 15G: revisão visual pública", conteudo)
        self.assertIn("home-action-card h2", conteudo)
        self.assertIn("dimension-grid", conteudo)
        self.assertIn("reference-grid", conteudo)

    def test_alt_do_rodape_muda_em_ingles(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertIn(
            "German Cooperation, GIZ, AdaptaInfra, OLACEFS, COMTEMA and CGID",
            conteudo,
        )
        self.assertNotIn("Coopera&ccedil;&atilde;o Alem&atilde;", conteudo)
