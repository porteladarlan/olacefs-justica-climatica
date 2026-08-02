from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class FidelidadeMeuEspacoTests(TestCase):
    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    @staticmethod
    def _localized_url(prefixo, nome):
        with translation.override("pt-br"):
            return f"{prefixo}{reverse(nome)}"

    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="usuario-fidelidade-espaco",
            email="usuario@example.org",
            password="SenhaForte123!",
        )

    def test_login_e_cadastro_usam_composicao_acessivel_trilingue(self):
        casos = (
            ("", "Entrar", "Criar uma conta"),
            ("/es", "Entrar", "Crear una cuenta"),
            ("/en", "Sign in", "Create an account"),
        )
        for prefixo, titulo_login, link_cadastro in casos:
            with self.subTest(prefixo=prefixo):
                response = self.client.get(
                    self._localized_url(prefixo, "login_usuario")
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    'class="account-page account-page--narrow"',
                    html=False,
                )
                self.assertContains(response, "praticas/css/meu-espaco")
                self.assertContains(response, titulo_login)
                self.assertContains(response, link_cadastro)
                self.assertContains(response, "csrfmiddlewaretoken")

                cadastro = self.client.get(
                    self._localized_url(prefixo, "registrar_usuario")
                )
                self.assertEqual(cadastro.status_code, 200)
                self.assertContains(cadastro, 'name="username"')
                self.assertContains(cadastro, 'name="password1"')
                self.assertContains(cadastro, 'name="password2"')
                self.assertContains(cadastro, "csrfmiddlewaretoken")

    def test_rotas_privadas_exigem_autenticacao(self):
        for nome in (
            "meus_envios",
            "status_envio",
            "adicionar_boa_pratica",
        ):
            with self.subTest(nome=nome):
                response = self.client.get(reverse(nome))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login_usuario"), response.url)

    def test_estado_vazio_autenticado_e_trilingue(self):
        self.client.force_login(self.usuario)
        casos = (
            (
                "",
                "Ainda não há envios vinculados à sua conta autenticada.",
                "Enviar nova pr&aacute;tica",
            ),
            (
                "/es",
                "Aún no hay envíos vinculados a su cuenta autenticada.",
                "Enviar nueva pr&aacute;ctica",
            ),
            (
                "/en",
                "No submissions are linked to your authenticated account yet.",
                "Submit new practice",
            ),
        )
        for prefixo, estado_vazio, cta in casos:
            for nome in ("meus_envios", "status_envio"):
                with self.subTest(prefixo=prefixo, nome=nome):
                    response = self.client.get(self._localized_url(prefixo, nome))
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, estado_vazio)
                    self.assertContains(response, cta)
                    self.assertNotContains(response, "vinculados ao e-mail")
                    self.assertNotContains(response, "linked to the e-mail")

    def test_formulario_de_envio_preserva_contratos_reais(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse("adicionar_boa_pratica"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="submission-page"', html=False)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(
            response,
            'name="acao_envio" value="rascunho"',
            html=False,
        )
        self.assertContains(
            response,
            'name="acao_envio" value="enviar"',
            html=False,
        )
        self.assertContains(response, 'name="pessoa_responsavel"')
        self.assertContains(response, 'name="anexo_arquivo_1"')
        self.assertContains(response, 'name="anexo_url_1"')
