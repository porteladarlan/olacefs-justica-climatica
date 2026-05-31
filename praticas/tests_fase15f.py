from django.test import TestCase
from django.urls import reverse


class SaneamentoTextosPublicosTests(TestCase):
    def test_sobre_nao_exibe_mvp(self):
        response = self.client.get(reverse("sobre_plataforma"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("MVP", conteudo)

    def test_comparador_nao_exibe_contribuicao_para_guia(self):
        response = self.client.get(reverse("comparar_experiencias"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("Contribution to the Guide", conteudo)
        self.assertNotIn("Contribución a la Guía", conteudo)
        self.assertNotIn("Contribui", conteudo)

    def test_favoritos_nao_usa_guia_como_finalidade(self):
        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            conteudo = response.content.decode("utf-8")
            self.assertNotIn("for the Guide", conteudo)
            self.assertNotIn("para la Gu", conteudo)
            self.assertNotIn("para a Guia", conteudo)
