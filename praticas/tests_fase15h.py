from django.contrib.auth import get_user_model
from django.test import TestCase


class FormularioEnvioRetroalimentacaoTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="autor_fase15h",
            email="autor_fase15h@example.org",
            password="teste123",
        )
        self.client.force_login(self.usuario)

    def test_formulario_envio_exibe_orientacao_de_fluxo_e_campos_obrigatorios(self):
        response = self.client.get("/adicionar-boa-pratica/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn("Rascunho", conteudo)
        self.assertIn("Enviar para revisão", conteudo)
        self.assertIn("Conteúdo público", conteudo)
        self.assertIn("Obrigatório", conteudo)
        self.assertIn("Pessoa responsável", conteudo)

    def test_formulario_envio_nao_exibe_campo_contribuicao_para_guia(self):
        response = self.client.get("/adicionar-boa-pratica/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertNotIn("contribui_para_guia", conteudo)
        self.assertNotIn("Contribui para a Guia", conteudo)
        self.assertNotIn("Contribution to the Guide", conteudo)
        self.assertNotIn("Contribución a la Guía", conteudo)

    def test_formulario_envio_em_ingles_mantem_orientacao_trilingue(self):
        response = self.client.get("/en/adicionar-boa-pratica/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn("Draft", conteudo)
        self.assertIn("Submit for review", conteudo)
        self.assertIn("Public content", conteudo)
        self.assertIn("Required", conteudo)
        self.assertIn("Responsible person", conteudo)
        self.assertIn("Methodologies, matrices or instruments used", conteudo)
