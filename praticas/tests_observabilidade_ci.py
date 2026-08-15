from unittest.mock import patch

from django.db import DatabaseError, InterfaceError
from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_get_saudavel_retorna_200(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)

    def test_get_saudavel_retorna_json_minimo(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(
            response.json(),
            {"status": "ok", "database": "ok"},
        )

    def test_get_saudavel_nao_permite_cache(self):
        response = self.client.get(reverse("health"))

        diretivas = response.headers["Cache-Control"]
        self.assertIn("max-age=0", diretivas)
        self.assertIn("no-cache", diretivas)
        self.assertIn("no-store", diretivas)
        self.assertIn("must-revalidate", diretivas)

    @patch("config.health.connection.cursor")
    def test_falha_do_banco_retorna_503(self, cursor_mock):
        cursor_mock.side_effect = DatabaseError("database unavailable")

        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "error", "database": "unavailable"},
        )

    @patch("config.health.connection.cursor")
    def test_erro_de_interface_do_banco_retorna_503(self, cursor_mock):
        cursor_mock.side_effect = InterfaceError("connection closed")

        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "error", "database": "unavailable"},
        )

    @patch("config.health.connection.cursor")
    def test_falha_do_banco_nao_expoe_informacoes_sensiveis(self, cursor_mock):
        informacoes_sensiveis = (
            "postgresql://usuario:senha@db.internal.example:5432/plataforma "
            "SECRET_KEY=segredo-interno"
        )
        cursor_mock.side_effect = DatabaseError(informacoes_sensiveis)

        response = self.client.get(reverse("health"))
        conteudo = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 503)
        for trecho in (
            "postgresql://",
            "usuario",
            "senha",
            "db.internal.example",
            "SECRET_KEY",
            "segredo-interno",
        ):
            with self.subTest(trecho=trecho):
                self.assertNotIn(trecho, conteudo)

    def test_somente_get_e_permitido(self):
        url = reverse("health")

        for metodo in ("head", "post", "put", "patch", "delete", "options"):
            with self.subTest(metodo=metodo):
                response = getattr(self.client, metodo)(url)
                self.assertEqual(response.status_code, 405)
                self.assertEqual(response.headers["Allow"], "GET")
