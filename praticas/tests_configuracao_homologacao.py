import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class ConfiguracaoHomologacaoTests(SimpleTestCase):
    variaveis_configuracao = {
        "DJANGO_ENV",
        "DEBUG",
        "SECRET_KEY",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "DATABASE_URL",
        "SESSION_COOKIE_SECURE",
        "CSRF_COOKIE_SECURE",
        "TRUST_X_FORWARDED_PROTO",
        "EMAIL_BACKEND",
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "EMAIL_USE_TLS",
        "EMAIL_USE_SSL",
        "EMAIL_TIMEOUT",
        "DEFAULT_FROM_EMAIL",
    }

    def _executar_settings(self, variaveis=None, codigo="import config.settings"):
        ambiente = os.environ.copy()
        for nome in self.variaveis_configuracao:
            ambiente.pop(nome, None)
        ambiente.update(variaveis or {})
        return subprocess.run(
            [sys.executable, "-c", codigo],
            cwd=settings.BASE_DIR,
            env=ambiente,
            capture_output=True,
            text=True,
            check=False,
        )

    def _ambiente_staging_valido(self):
        return {
            "DJANGO_ENV": "staging",
            "DEBUG": "False",
            "SECRET_KEY": "test-only-" + ("x" * 60),
            "ALLOWED_HOSTS": "homologacao.example.invalid",
            "CSRF_TRUSTED_ORIGINS": "https://homologacao.example.invalid",
            "DATABASE_URL": (
                "postgresql://placeholder:placeholder@db.example.invalid/placeholder"
            ),
        }

    def test_desenvolvimento_mantem_sqlite_e_defaults_locais(self):
        codigo = """
import json
import config.settings as configuracao
print(json.dumps({
    "ambiente": configuracao.DJANGO_ENV,
    "hosts": configuracao.ALLOWED_HOSTS,
    "csrf": configuracao.CSRF_TRUSTED_ORIGINS,
    "engine": configuracao.DATABASES["default"]["ENGINE"],
    "proxy": hasattr(configuracao, "SECURE_PROXY_SSL_HEADER"),
}))
"""
        resultado = self._executar_settings(codigo=codigo)

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        configuracao = json.loads(resultado.stdout)
        self.assertEqual(configuracao["ambiente"], "development")
        self.assertEqual(configuracao["hosts"], ["127.0.0.1", "localhost"])
        self.assertEqual(configuracao["csrf"], [])
        self.assertEqual(configuracao["engine"], "django.db.backends.sqlite3")
        self.assertFalse(configuracao["proxy"])

    def test_staging_exige_variaveis_criticas_explicitas(self):
        resultado = self._executar_settings({"DJANGO_ENV": "staging"})

        self.assertNotEqual(resultado.returncode, 0)
        for nome in (
            "DEBUG",
            "SECRET_KEY",
            "ALLOWED_HOSTS",
            "CSRF_TRUSTED_ORIGINS",
            "DATABASE_URL",
        ):
            self.assertIn(nome, resultado.stderr)

    def test_staging_valido_usa_postgresql_cookies_seguros_e_proxy_opt_in(self):
        variaveis = self._ambiente_staging_valido()
        variaveis["TRUST_X_FORWARDED_PROTO"] = "True"
        codigo = """
import json
import config.settings as configuracao
print(json.dumps({
    "engine": configuracao.DATABASES["default"]["ENGINE"],
    "session_secure": configuracao.SESSION_COOKIE_SECURE,
    "csrf_secure": configuracao.CSRF_COOKIE_SECURE,
    "proxy": configuracao.SECURE_PROXY_SSL_HEADER,
}))
"""
        resultado = self._executar_settings(variaveis, codigo)

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        configuracao = json.loads(resultado.stdout)
        self.assertEqual(configuracao["engine"], "django.db.backends.postgresql")
        self.assertTrue(configuracao["session_secure"])
        self.assertTrue(configuracao["csrf_secure"])
        self.assertEqual(
            configuracao["proxy"], ["HTTP_X_FORWARDED_PROTO", "https"]
        )

    def test_staging_rejeita_configuracao_insegura(self):
        cenarios = (
            ("debug", {"DEBUG": "True"}, "DEBUG deve permanecer False"),
            (
                "secret_key_fraca",
                {"SECRET_KEY": "django-insecure-fraca"},
                "SECRET_KEY deve ser longa, aleatória e exclusiva",
            ),
            ("host_coringa", {"ALLOWED_HOSTS": "*"}, "não pode usar '*'"),
            (
                "csrf_http",
                {"CSRF_TRUSTED_ORIGINS": "http://homologacao.example.invalid"},
                "somente origens HTTPS",
            ),
            (
                "cookie_sessao",
                {"SESSION_COOKIE_SECURE": "False"},
                "Cookies de sessão e CSRF",
            ),
            (
                "sqlite",
                {"DATABASE_URL": "sqlite:///temporary.sqlite3"},
                "SQLite não é permitido",
            ),
        )

        for nome, sobrescritas, mensagem in cenarios:
            with self.subTest(cenario=nome):
                variaveis = self._ambiente_staging_valido()
                variaveis.update(sobrescritas)
                resultado = self._executar_settings(variaveis)

                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(mensagem, resultado.stderr)

    def test_email_usa_console_por_padrao_e_aceita_configuracao_smtp(self):
        codigo = """
import json
import config.settings as configuracao
print(json.dumps({
    "backend": configuracao.EMAIL_BACKEND,
    "port": configuracao.EMAIL_PORT,
    "tls": configuracao.EMAIL_USE_TLS,
    "ssl": configuracao.EMAIL_USE_SSL,
    "timeout": configuracao.EMAIL_TIMEOUT,
}))
"""
        local = self._executar_settings(codigo=codigo)
        self.assertEqual(local.returncode, 0, local.stderr)
        self.assertEqual(
            json.loads(local.stdout)["backend"],
            "django.core.mail.backends.console.EmailBackend",
        )

        smtp = self._executar_settings(
            {
                "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "EMAIL_PORT": "587",
                "EMAIL_USE_TLS": "True",
                "EMAIL_USE_SSL": "False",
                "EMAIL_TIMEOUT": "15",
            },
            codigo,
        )
        self.assertEqual(smtp.returncode, 0, smtp.stderr)
        configuracao = json.loads(smtp.stdout)
        self.assertEqual(configuracao["port"], 587)
        self.assertTrue(configuracao["tls"])
        self.assertFalse(configuracao["ssl"])
        self.assertEqual(configuracao["timeout"], 15)

    def test_email_rejeita_inteiro_invalido_e_tls_com_ssl(self):
        porta = self._executar_settings({"EMAIL_PORT": "smtp"})
        self.assertNotEqual(porta.returncode, 0)
        self.assertIn("EMAIL_PORT deve ser um número inteiro", porta.stderr)

        protocolos = self._executar_settings(
            {"EMAIL_USE_TLS": "True", "EMAIL_USE_SSL": "True"}
        )
        self.assertNotEqual(protocolos.returncode, 0)
        self.assertIn(
            "EMAIL_USE_TLS e EMAIL_USE_SSL não podem estar ativos simultaneamente",
            protocolos.stderr,
        )
