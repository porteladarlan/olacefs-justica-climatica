from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class RecursosTecnicosRetroalimentacaoTests(TestCase):
    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    def test_recursos_tecnicos_exibe_biblioteca_com_estado_vazio_honesto(self):
        response = self.client.get(reverse("banco_tecnico"))

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn('class="norm-library"', conteudo)
        self.assertIn('name="q"', conteudo)
        self.assertEqual(response.context["total_resultados"], 0)
        self.assertIn("Ainda n&atilde;o h&aacute; recursos institucionais publicados", conteudo)

    def test_recursos_tecnicos_nao_chama_conteudo_provisorio_de_final(self):
        response = self.client.get(reverse("banco_tecnico"))

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("conteúdo final publicado", conteudo.lower())
        self.assertNotIn("contenido final publicado", conteudo.lower())
        self.assertNotIn("final published content", conteudo.lower())
