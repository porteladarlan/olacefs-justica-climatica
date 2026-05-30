from django.test import TestCase
from django.urls import reverse


class RecursosTecnicosRetroalimentacaoTests(TestCase):
    def test_recursos_tecnicos_exibe_conteudo_em_desenvolvimento(self):
        response = self.client.get(reverse("banco_tecnico"))

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertTrue(
            "Conte&uacute;do em desenvolvimento" in conteudo
            or "Contenido en desarrollo" in conteudo
            or "Content under development" in conteudo
        )
        self.assertTrue(
            "consultoria auditora especializada" in conteudo
            or "consultor&iacute;a auditora especializada" in conteudo
            or "specialized audit consultancy" in conteudo
        )
        self.assertTrue(
            "laborat&oacute;rio de justi&ccedil;a clim&aacute;tica" in conteudo
            or "laboratorio de justicia clim&aacute;tica" in conteudo
            or "climate justice laboratory" in conteudo
        )

    def test_recursos_tecnicos_nao_chama_conteudo_provisorio_de_final(self):
        response = self.client.get(reverse("banco_tecnico"))

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("conteúdo final publicado", conteudo.lower())
        self.assertNotIn("contenido final publicado", conteudo.lower())
        self.assertNotIn("final published content", conteudo.lower())
