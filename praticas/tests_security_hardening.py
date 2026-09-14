from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SecurityHardeningTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="security-hardening",
            password="senha-teste-segura",
        )

    def test_logout_rejeita_get_sem_encerrar_sessao(self):
        self.client.force_login(self.usuario)

        response = self.client.get(reverse("logout_usuario"))

        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_post_exige_autenticacao(self):
        response = self.client.post(reverse("logout_usuario"))

        self.assertRedirects(
            response,
            f'{reverse("login_usuario")}?next={reverse("logout_usuario")}',
            fetch_redirect_response=False,
        )

    def test_logout_post_encerra_sessao(self):
        self.client.force_login(self.usuario)

        response = self.client.post(reverse("logout_usuario"))

        self.assertRedirects(response, reverse("pagina_inicial"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_headers_csp_sao_emitidos(self):
        response = self.client.get(reverse("pagina_inicial"))

        politica = response.headers["Content-Security-Policy"]
        self.assertIn("base-uri 'self'", politica)
        self.assertIn("form-action 'self'", politica)
        self.assertIn("frame-ancestors 'none'", politica)
        self.assertIn("object-src 'none'", politica)

        relatorio = response.headers["Content-Security-Policy-Report-Only"]
        self.assertIn("default-src 'self'", relatorio)
        self.assertIn("https://cdn.jsdelivr.net", relatorio)

    def test_parametros_defensivos_de_sessao_e_token(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, "Lax")
        self.assertEqual(settings.CSRF_COOKIE_SAMESITE, "Lax")
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertEqual(settings.SESSION_COOKIE_AGE, 8 * 60 * 60)
        self.assertEqual(settings.PASSWORD_RESET_TIMEOUT, 24 * 60 * 60)
