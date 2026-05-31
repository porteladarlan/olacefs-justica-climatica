from django.test import TestCase
from django.urls import reverse


class SaneamentoTextosPublicosTests(TestCase):
    def test_sobre_nao_exibe_mvp(self):
        response = self.client.get(reverse("sobre_plataforma"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("MVP", conteudo)
        self.assertNotIn("mvp", conteudo)

    def test_favoritos_nao_exibe_referencia_a_guia_como_finalidade(self):
        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("exemplos para a Guia", conteudo)
        self.assertNotIn("ejemplos para la Gu", conteudo)
        self.assertNotIn("examples for the Guide", conteudo)

    def test_comparador_nao_exibe_contribuicao_para_guia(self):
        response = self.client.get(reverse("comparar_experiencias"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("Contribution to the Guide", conteudo)
        self.assertNotIn("Contribuci", conteudo)
        self.assertNotIn("Contribui", conteudo)

    def test_revisao_usa_metodologias_em_vez_de_ferramentas(self):
        # Este teste valida o template estaticamente porque a rota exige dados e permissão.
        caminho = "templates/praticas/revisar_experiencia.html"
        with open(caminho, encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
        self.assertIn("metodologias", conteudo.lower())
        self.assertNotIn("Perguntas, critérios e ferramentas", conteudo)
        self.assertNotIn("Ferramentas e metodologias", conteudo)
