import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase


HELPER_PATH = Path(settings.BASE_DIR) / "ops" / "postgres_client.py"
SPEC = importlib.util.spec_from_file_location("postgres_client", HELPER_PATH)
postgres_client = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(postgres_client)


class PostgresClientTests(SimpleTestCase):
    def test_uri_basica_gera_variaveis_libpq(self):
        environment = postgres_client.parse_database_url(
            "postgresql://usuario:senha@host:5432/banco"
        )

        self.assertEqual(
            environment,
            {
                "PGHOST": "host",
                "PGPORT": "5432",
                "PGUSER": "usuario",
                "PGPASSWORD": "senha",
                "PGDATABASE": "banco",
            },
        )

    def test_percent_encoding_em_usuario_senha_e_banco(self):
        environment = postgres_client.parse_database_url(
            "postgresql://usu%40rio:s%2Fen%3Aha@host/banco%20clima"
        )

        self.assertEqual(environment["PGUSER"], "usu@rio")
        self.assertEqual(environment["PGPASSWORD"], "s/en:ha")
        self.assertEqual(environment["PGDATABASE"], "banco clima")

    def test_scheme_postgres_e_aceito(self):
        environment = postgres_client.parse_database_url(
            "postgres://usuario:senha@host/banco"
        )

        self.assertEqual(environment["PGDATABASE"], "banco")

    def test_porta_ausente_nao_define_pgport(self):
        environment = postgres_client.parse_database_url(
            "postgresql://usuario:senha@host/banco"
        )

        self.assertNotIn("PGPORT", environment)

    def test_sslmode_e_mapeado(self):
        environment = postgres_client.parse_database_url(
            "postgresql://usuario:senha@host/banco?sslmode=require"
        )

        self.assertEqual(environment["PGSSLMODE"], "require")

    def test_parametros_permitidos_sao_mapeados(self):
        environment = postgres_client.parse_database_url(
            "postgresql://usuario:senha@host/banco"
            "?sslrootcert=%2Fcerts%2Froot.pem"
            "&sslcert=%2Fcerts%2Fclient.pem"
            "&sslkey=%2Fcerts%2Fclient.key"
            "&connect_timeout=10"
            "&application_name=backup"
            "&target_session_attrs=read-write"
        )

        self.assertEqual(environment["PGSSLROOTCERT"], "/certs/root.pem")
        self.assertEqual(environment["PGSSLCERT"], "/certs/client.pem")
        self.assertEqual(environment["PGSSLKEY"], "/certs/client.key")
        self.assertEqual(environment["PGCONNECT_TIMEOUT"], "10")
        self.assertEqual(environment["PGAPPNAME"], "backup")
        self.assertEqual(environment["PGTARGETSESSIONATTRS"], "read-write")

    def test_parametro_desconhecido_e_rejeitado(self):
        with self.assertRaises(postgres_client.ConfigurationError):
            postgres_client.parse_database_url(
                "postgresql://usuario:senha@host/banco?options=-c%20search_path%3Dpublic"
            )

    def test_parametro_duplicado_e_rejeitado(self):
        with self.assertRaises(postgres_client.ConfigurationError):
            postgres_client.parse_database_url(
                "postgresql://usuario:senha@host/banco?sslmode=require&sslmode=verify-full"
            )

    def test_scheme_invalido_e_rejeitado(self):
        with self.assertRaises(postgres_client.ConfigurationError):
            postgres_client.parse_database_url(
                "mysql://usuario:senha@host:3306/banco"
            )

    def test_database_url_ausente_e_rejeitada_sem_expor_ambiente(self):
        environment = os.environ.copy()
        environment.pop("DATABASE_URL", None)

        result = subprocess.run(
            [sys.executable, str(HELPER_PATH), sys.executable, "-c", "pass"],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("DATABASE_URL não está definida", result.stderr)

    def test_database_url_nao_e_repassada_e_credenciais_nao_entram_no_argv(self):
        database_url = "postgresql://usuario:senha-secreta@host:5432/banco"
        original_environment = {
            "DATABASE_URL": database_url,
            "PATH": os.environ.get("PATH", ""),
            "PGPASSWORD": "valor-antigo",
        }

        with mock.patch.object(postgres_client.os, "environ", original_environment):
            with mock.patch.object(postgres_client.subprocess, "run") as run:
                run.return_value.returncode = 0
                postgres_client.main(["pg_dump", "--format=custom"])

        arguments = run.call_args.args[0]
        child_environment = run.call_args.kwargs["env"]
        self.assertEqual(arguments, ["pg_dump", "--format=custom"])
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertNotIn("DATABASE_URL", child_environment)
        self.assertEqual(child_environment["PGPASSWORD"], "senha-secreta")
        self.assertNotIn(database_url, arguments)
        self.assertNotIn("senha-secreta", arguments)

    def test_configuracoes_pg_herdadas_sao_removidas(self):
        child_environment = postgres_client.build_client_environment(
            {
                "DATABASE_URL": "postgresql://usuario:senha-nova@host-novo/banco",
                "PATH": "/usr/local/bin:/usr/bin",
                "PGHOST": "host-antigo",
                "PGHOSTADDR": "192.0.2.10",
                "PGPASSWORD": "senha-antiga",
                "PGSERVICE": "servico-antigo",
                "PGPASSFILE": "/arquivo/antigo",
                "PGOPTIONS": "-c search_path=outro",
            }
        )

        self.assertEqual(child_environment["PGHOST"], "host-novo")
        self.assertEqual(child_environment["PGPASSWORD"], "senha-nova")
        self.assertNotIn("PGHOSTADDR", child_environment)
        self.assertNotIn("PGSERVICE", child_environment)
        self.assertNotIn("PGPASSFILE", child_environment)
        self.assertNotIn("PGOPTIONS", child_environment)
        self.assertNotIn("DATABASE_URL", child_environment)
        self.assertEqual(child_environment["PATH"], "/usr/local/bin:/usr/bin")

    def test_exit_code_do_cliente_e_preservado(self):
        environment = os.environ.copy()
        environment["DATABASE_URL"] = (
            "postgresql://usuario:senha@host:5432/banco"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(HELPER_PATH),
                sys.executable,
                "-c",
                "raise SystemExit(37)",
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 37)

    def test_scripts_usam_helper_sem_uri_em_pgdatabase(self):
        for script_name in ("backup-postgres.sh", "restore-postgres.sh"):
            with self.subTest(script=script_name):
                content = (Path(settings.BASE_DIR) / "ops" / script_name).read_text(
                    encoding="utf-8"
                )
                self.assertIn('"$POSTGRES_CLIENT_HELPER"', content)
                self.assertNotIn('PGDATABASE="$database_connection"', content)

    def test_pg_restore_list_permanece_sem_conexao(self):
        content = (Path(settings.BASE_DIR) / "ops" / "restore-postgres.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn('"$PG_RESTORE_BIN" --list "$DUMP_PATH"', content)
