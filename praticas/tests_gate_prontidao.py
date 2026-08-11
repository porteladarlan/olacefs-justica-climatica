import os
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class GateProntidaoTests(SimpleTestCase):
    staging_saudavel = {
        "DJANGO_ENV": "staging",
        "DEBUG": False,
        "SECRET_KEY": "test-only-" + ("x" * 60),
        "ALLOWED_HOSTS": ["homologacao.example.invalid"],
        "CSRF_TRUSTED_ORIGINS": ["https://homologacao.example.invalid"],
        "SESSION_COOKIE_SECURE": True,
        "CSRF_COOKIE_SECURE": True,
        "SECURE_SSL_REDIRECT": False,
        "SECURE_HSTS_SECONDS": 0,
    }

    def _executar_gate(self, **opcoes):
        saida = StringIO()
        call_command("checar_prontidao_ambiente", stdout=saida, **opcoes)
        return saida.getvalue()

    @override_settings(
        DJANGO_ENV="development",
        DEBUG=True,
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
    )
    def test_development_local_saudavel_permite_sqlite_e_defaults(self):
        with patch.object(
            settings,
            "DATABASES",
            {"default": {"ENGINE": "django.db.backends.sqlite3"}},
        ), patch.dict(os.environ, {"TRUST_X_FORWARDED_PROTO": "False"}):
            saida = self._executar_gate(falhar=True)

        self.assertIn("ambiente local/teste", saida)
        self.assertIn("SQLite permitido", saida)
        self.assertIn("Variáveis e infraestrutura de produção não são exigidas", saida)
        self.assertIn("Checagem concluída sem falhas críticas", saida)

    def test_staging_saudavel_sintetico(self):
        configuracao = {
            **self.staging_saudavel,
            "SECURE_PROXY_SSL_HEADER": (
                "HTTP_X_FORWARDED_PROTO",
                "https",
            ),
        }
        with override_settings(**configuracao), patch.object(
            settings,
            "DATABASES",
            {"default": {"ENGINE": "django.db.backends.postgresql"}},
        ), patch.dict(os.environ, {"TRUST_X_FORWARDED_PROTO": "True"}):
            saida = self._executar_gate(falhar=True)

        self.assertIn("staging/production: validações de implantação ativas", saida)
        self.assertIn("DATABASE_URL/banco carregado não usa SQLite", saida)
        self.assertIn("Proxy SSL habilitado explicitamente", saida)
        self.assertIn("Checagem concluída sem falhas críticas", saida)

    def test_configuracao_critica_invalida_e_detectada(self):
        configuracao = {
            **self.staging_saudavel,
            "DEBUG": True,
            "SECRET_KEY": "",
            "ALLOWED_HOSTS": [],
            "CSRF_TRUSTED_ORIGINS": ["http://homologacao.example.invalid"],
            "SESSION_COOKIE_SECURE": False,
            "CSRF_COOKIE_SECURE": False,
        }
        saida = StringIO()

        with override_settings(**configuracao), patch.object(
            settings,
            "DATABASES",
            {"default": {"ENGINE": "django.db.backends.sqlite3"}},
        ), patch.dict(
            os.environ, {"TRUST_X_FORWARDED_PROTO": "False"}
        ), self.assertRaises(SystemExit):
            call_command(
                "checar_prontidao_ambiente",
                falhar=True,
                stdout=saida,
            )

        diagnostico = saida.getvalue()
        for mensagem in (
            "DEBUG deve permanecer False",
            "SECRET_KEY não configurada",
            "ALLOWED_HOSTS deve ser explícito",
            "CSRF_TRUSTED_ORIGINS deve conter origens HTTPS",
            "DATABASE_URL deve configurar banco não SQLite",
            "SESSION_COOKIE_SECURE deve ser True",
            "CSRF_COOKIE_SECURE deve ser True",
        ):
            with self.subTest(mensagem=mensagem):
                self.assertIn(mensagem, diagnostico)

    def test_pendencias_externas_e_https_nao_bloqueiam_gate(self):
        with override_settings(**self.staging_saudavel), patch.object(
            settings,
            "DATABASES",
            {"default": {"ENGINE": "django.db.backends.postgresql"}},
        ), patch.dict(os.environ, {"TRUST_X_FORWARDED_PROTO": "False"}):
            saida = self._executar_gate(falhar=True)

        self.assertIn("AVISO  SECURE_SSL_REDIRECT ainda não habilitado", saida)
        self.assertIn("AVISO  HSTS ainda não habilitado", saida)
        self.assertIn("Pendências institucionais externas", saida)
        self.assertIn("Storage persistente para anexos", saida)
        self.assertIn("Logs centralizados e monitoramento", saida)
        self.assertIn("Checagem concluída sem falhas críticas", saida)

    @patch("praticas.management.commands.validar_entrega_final.call_command")
    def test_validar_entrega_final_propaga_falha_critica_com_falhar(
        self, executar_comando
    ):
        def executar(nome, **opcoes):
            if nome == "checar_prontidao_ambiente":
                raise SystemExit(1)

        executar_comando.side_effect = executar

        with self.assertRaises(SystemExit):
            call_command("validar_entrega_final", falhar=True, stdout=StringIO())

        executar_comando.assert_any_call(
            "checar_prontidao_ambiente", falhar=True
        )

    @patch("praticas.management.commands.validar_entrega_final.call_command")
    def test_validar_entrega_final_registra_falha_tecnica_sem_interromper(
        self, executar_comando
    ):
        def executar(nome, **opcoes):
            if nome == "checar_prontidao_ambiente":
                raise SystemExit(1)

        executar_comando.side_effect = executar
        saida = StringIO()

        call_command("validar_entrega_final", stdout=saida)

        self.assertIn("ALERTA: Checagem de prontidão técnica", saida.getvalue())
        self.assertIn("concluída com 1 ocorrência", saida.getvalue())
