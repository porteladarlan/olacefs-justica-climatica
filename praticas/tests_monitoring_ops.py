import importlib.util
import os
import smtplib
import ssl
import stat
import sys
import tempfile
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase


MONITOR_PATH = Path(settings.BASE_DIR) / "ops" / "monitor.py"
SPEC = importlib.util.spec_from_file_location("operational_monitor", MONITOR_PATH)
monitor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = monitor
SPEC.loader.exec_module(monitor)

FIXED_NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)


class MonitoringOpsTests(SimpleTestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temporary_directory.name).resolve()
        self.postgres_path = self.base_path / "postgres"
        self.media_path = self.base_path / "media"
        self.postgres_path.mkdir()
        self.media_path.mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def valid_environment(self):
        return {
            "MONITOR_ENVIRONMENT": "staging",
            "MONITOR_HEALTH_URL": "https://staging.example.invalid/health/",
            "MONITOR_ALERT_RECIPIENTS": "ops1@example.invalid,ops2@example.invalid",
            "MONITOR_SMTP_HOST": "smtp.example.invalid",
            "MONITOR_SMTP_PORT": "587",
            "MONITOR_SMTP_USE_TLS": "true",
            "MONITOR_SMTP_USER": "monitor@example.invalid",
            "MONITOR_SMTP_PASSWORD": "smtp-test-password",
            "MONITOR_FROM_EMAIL": "monitor@example.invalid",
            "MONITOR_TIMEOUT_SECONDS": "10",
            "MONITOR_BACKUP_MAX_AGE_SECONDS": "129600",
            "MONITOR_DISK_WARNING_PERCENT": "80",
            "MONITOR_DISK_CRITICAL_PERCENT": "90",
            "MONITOR_ALERT_REPEAT_SECONDS": "21600",
            "MONITOR_STATE_FILE": str(self.base_path / "state" / "monitor.json"),
            "MONITOR_POSTGRES_BACKUP_DIR": str(self.postgres_path),
            "MONITOR_MEDIA_BACKUP_DIR": str(self.media_path),
            "MONITOR_DISK_PATH": str(self.base_path),
        }

    def config(self):
        return monitor.MonitorConfig.from_environment(self.valid_environment())

    def check(self, status, check_id="test_check", message="mensagem sanitizada"):
        return monitor.result(check_id, status, message, now=FIXED_NOW)

    def create_backup(self, directory, prefix, suffix, age_hours=1, size=7):
        timestamp = (FIXED_NOW - timedelta(hours=age_hours)).strftime(
            "%Y%m%dT%H%M%SZ"
        )
        backup_path = directory / f"{prefix}{timestamp}{suffix}"
        backup_path.write_bytes(b"x" * size)
        Path(f"{backup_path}.sha256").write_text(
            f"fakehash  {backup_path.name}\n", encoding="utf-8"
        )
        return backup_path

    def systemd_runner(self, *, active="active", loaded="loaded"):
        return mock.Mock(
            return_value=monitor.CommandResult(
                0,
                f"LoadState={loaded}\nActiveState={active}\nSubState=running\n",
            )
        )

    def timer_runner(self, *, enabled="enabled", active="active", schedule="tomorrow"):
        def run(arguments, timeout):
            del timeout
            if "is-enabled" in arguments:
                return monitor.CommandResult(0 if enabled == "enabled" else 1, enabled)
            if "is-active" in arguments:
                return monitor.CommandResult(0 if active == "active" else 3, active)
            return monitor.CommandResult(0, schedule)

        return mock.Mock(side_effect=run)

    def test_configuracao_valida_aplica_defaults_seguros(self):
        environment = self.valid_environment()
        for name in (
            "MONITOR_SMTP_PORT",
            "MONITOR_SMTP_USE_TLS",
            "MONITOR_TIMEOUT_SECONDS",
            "MONITOR_BACKUP_MAX_AGE_SECONDS",
            "MONITOR_DISK_WARNING_PERCENT",
            "MONITOR_DISK_CRITICAL_PERCENT",
            "MONITOR_ALERT_REPEAT_SECONDS",
        ):
            environment.pop(name)

        config = monitor.MonitorConfig.from_environment(environment)

        self.assertEqual(config.smtp_port, 587)
        self.assertTrue(config.smtp_use_tls)
        self.assertEqual(config.timeout_seconds, 10)
        self.assertEqual(config.backup_max_age_seconds, 129600)
        self.assertEqual(config.disk_warning_percent, 80)
        self.assertEqual(config.disk_critical_percent, 90)
        self.assertEqual(config.alert_repeat_seconds, 21600)
        self.assertEqual(
            config.alert_recipients,
            ("ops1@example.invalid", "ops2@example.invalid"),
        )

    def test_configuracao_rejeita_thresholds_de_disco_invalidos(self):
        environment = self.valid_environment()
        environment["MONITOR_DISK_WARNING_PERCENT"] = "90"
        environment["MONITOR_DISK_CRITICAL_PERCENT"] = "80"

        with self.assertRaises(monitor.ConfigurationError):
            monitor.MonitorConfig.from_environment(environment)

    def test_configuracao_rejeita_health_sem_https(self):
        environment = self.valid_environment()
        environment["MONITOR_HEALTH_URL"] = "http://staging.example.invalid/health/"

        with self.assertRaises(monitor.ConfigurationError):
            monitor.MonitorConfig.from_environment(environment)

    def test_configuracao_rejeita_health_com_credenciais(self):
        environment = self.valid_environment()
        environment["MONITOR_HEALTH_URL"] = (
            "https://usuario:senha@staging.example.invalid/health/"
        )

        with self.assertRaises(monitor.ConfigurationError):
            monitor.MonitorConfig.from_environment(environment)

    def test_configuracao_rejeita_booleano_ambiguo(self):
        environment = self.valid_environment()
        environment["MONITOR_SMTP_USE_TLS"] = "talvez"

        with self.assertRaises(monitor.ConfigurationError):
            monitor.MonitorConfig.from_environment(environment)

    def test_configuracao_tls_true_e_valida(self):
        environment = self.valid_environment()
        environment["MONITOR_SMTP_USE_TLS"] = "true"

        config = monitor.MonitorConfig.from_environment(environment)

        self.assertTrue(config.smtp_use_tls)

    def test_configuracao_tls_false_e_rejeitada_sem_expor_senha(self):
        environment = self.valid_environment()
        environment["MONITOR_SMTP_USE_TLS"] = "false"

        with self.assertRaises(monitor.ConfigurationError) as raised:
            monitor.MonitorConfig.from_environment(environment)

        self.assertEqual(
            str(raised.exception),
            "MONITOR_SMTP_USE_TLS deve permanecer habilitado.",
        )
        self.assertNotIn("smtp-test-password", str(raised.exception))

    def test_configuracao_rejeita_smtp_obrigatorio_ausente(self):
        environment = self.valid_environment()
        environment.pop("MONITOR_SMTP_PASSWORD")

        with self.assertRaises(monitor.ConfigurationError):
            monitor.MonitorConfig.from_environment(environment)

    def test_servico_django_active_retorna_ok(self):
        result = monitor.check_systemd_service(
            "django_service",
            "justica-climatica.service",
            10,
            command_runner=self.systemd_runner(),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_servico_django_inactive_retorna_critical(self):
        result = monitor.check_systemd_service(
            "django_service",
            "justica-climatica.service",
            10,
            command_runner=self.systemd_runner(active="inactive"),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_servico_nginx_active_retorna_ok(self):
        result = monitor.check_systemd_service(
            "nginx_service",
            "nginx.service",
            10,
            command_runner=self.systemd_runner(),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_servico_nginx_nao_carregado_retorna_critical(self):
        result = monitor.check_systemd_service(
            "nginx_service",
            "nginx.service",
            10,
            command_runner=self.systemd_runner(loaded="not-found"),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_health_http_200_retorna_ok(self):
        response = mock.MagicMock()
        response.__enter__.return_value.getcode.return_value = 200

        result = monitor.check_health_endpoint(
            "https://example.invalid/health/",
            10,
            opener=mock.Mock(return_value=response),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)
        self.assertEqual(result.message, "HTTP 200")

    def test_health_timeout_retorna_critical(self):
        result = monitor.check_health_endpoint(
            "https://example.invalid/health/",
            10,
            opener=mock.Mock(side_effect=TimeoutError("host interno")),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertNotIn("host interno", result.message)

    def test_health_http_500_retorna_critical_sem_corpo(self):
        error = urllib.error.HTTPError(
            "https://example.invalid/health/", 500, "segredo no corpo", {}, None
        )

        result = monitor.check_health_endpoint(
            "https://example.invalid/health/",
            10,
            opener=mock.Mock(side_effect=error),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertEqual(result.message, "health endpoint retornou HTTP 500")
        self.assertNotIn("segredo", result.message)

    def test_health_erro_tls_retorna_critical_sanitizado(self):
        result = monitor.check_health_endpoint(
            "https://example.invalid/health/",
            10,
            opener=mock.Mock(side_effect=ssl.SSLError("certificado interno")),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertEqual(result.message, "health endpoint indisponível")

    def test_timer_postgres_enabled_e_active_retorna_ok(self):
        result = monitor.check_systemd_timer(
            "postgres_timer",
            "justica-backup-postgres.timer",
            10,
            command_runner=self.timer_runner(),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)
        self.assertIn("próxima execução", result.message)

    def test_timer_postgres_disabled_retorna_critical(self):
        result = monitor.check_systemd_timer(
            "postgres_timer",
            "justica-backup-postgres.timer",
            10,
            command_runner=self.timer_runner(enabled="disabled"),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_timer_media_active_retorna_ok(self):
        result = monitor.check_systemd_timer(
            "media_timer",
            "justica-backup-media.timer",
            10,
            command_runner=self.timer_runner(),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_timer_inactive_retorna_critical(self):
        result = monitor.check_systemd_timer(
            "media_timer",
            "justica-backup-media.timer",
            10,
            command_runner=self.timer_runner(active="inactive"),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_backup_postgres_recente_retorna_ok(self):
        self.create_backup(self.postgres_path, "justica-climatica-", ".dump")

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_backup_postgres_antigo_retorna_critical(self):
        self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump", age_hours=37
        )

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertIn("atrasado", result.message)

    def test_backup_dois_minutos_no_futuro_e_aceito_como_clock_skew(self):
        self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump", age_hours=-2 / 60
        )

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_backup_dez_minutos_no_futuro_retorna_critical(self):
        self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump", age_hours=-10 / 60
        )

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertEqual(result.message, "timestamp do último backup está no futuro")

    def test_backup_muito_futuro_nao_mascara_backup_atrasado(self):
        self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump", age_hours=37
        )
        self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump", age_hours=-24
        )

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertIn("futuro", result.message)

    def test_backup_postgres_inexistente_retorna_critical(self):
        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_backup_sem_checksum_retorna_critical(self):
        backup_path = self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump"
        )
        Path(f"{backup_path}.sha256").unlink()

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertIn("checksum", result.message)

    def test_backup_media_recente_retorna_ok(self):
        self.create_backup(
            self.media_path, "justica-climatica-media-", ".tar.gz"
        )

        result = monitor.check_latest_backup(
            "media_backup",
            self.media_path,
            monitor.MEDIA_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_backup_media_antigo_retorna_critical(self):
        self.create_backup(
            self.media_path,
            "justica-climatica-media-",
            ".tar.gz",
            age_hours=37,
        )

        result = monitor.check_latest_backup(
            "media_backup",
            self.media_path,
            monitor.MEDIA_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_backup_ignora_lock_temporario_e_nome_fora_do_padrao(self):
        (self.postgres_path / ".backup-postgres.lock").write_text("", encoding="utf-8")
        (self.postgres_path / "backup.tmp").write_text("conteúdo", encoding="utf-8")
        (self.postgres_path / "qualquer.dump").write_text("conteúdo", encoding="utf-8")

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertIn("nenhum backup válido", result.message)

    def test_backup_vazio_retorna_critical(self):
        self.create_backup(
            self.postgres_path, "justica-climatica-", ".dump", size=0
        )

        result = monitor.check_latest_backup(
            "postgres_backup",
            self.postgres_path,
            monitor.POSTGRES_BACKUP_PATTERN,
            129600,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertIn("vazio", result.message)

    def test_oneshot_inactive_apos_success_retorna_ok(self):
        runner = mock.Mock(
            return_value=monitor.CommandResult(
                0, "LoadState=loaded\nActiveState=inactive\nResult=success\n"
            )
        )

        result = monitor.check_oneshot_result(
            "postgres_backup_service",
            "justica-backup-postgres.service",
            10,
            command_runner=runner,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_oneshot_com_result_failed_retorna_critical(self):
        runner = mock.Mock(
            return_value=monitor.CommandResult(
                0, "LoadState=loaded\nActiveState=failed\nResult=exit-code\n"
            )
        )

        result = monitor.check_oneshot_result(
            "media_backup_service",
            "justica-backup-media.service",
            10,
            command_runner=runner,
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_disco_abaixo_do_warning_retorna_ok(self):
        result = monitor.check_disk_usage(
            self.base_path,
            80,
            90,
            disk_usage=mock.Mock(return_value=SimpleNamespace(total=100, used=79)),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.OK)

    def test_disco_entre_warning_e_critical_retorna_warning(self):
        result = monitor.check_disk_usage(
            self.base_path,
            80,
            90,
            disk_usage=mock.Mock(return_value=SimpleNamespace(total=100, used=85)),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.WARNING)

    def test_disco_no_critical_retorna_critical(self):
        result = monitor.check_disk_usage(
            self.base_path,
            80,
            90,
            disk_usage=mock.Mock(return_value=SimpleNamespace(total=100, used=90)),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)

    def test_falha_de_leitura_do_disco_retorna_critical(self):
        result = monitor.check_disk_usage(
            self.base_path,
            80,
            90,
            disk_usage=mock.Mock(side_effect=OSError("caminho interno")),
            now=FIXED_NOW,
        )

        self.assertEqual(result.status, monitor.CRITICAL)
        self.assertNotIn("caminho interno", result.message)

    def test_resultado_global_prioriza_critical_e_depois_warning(self):
        self.assertEqual(
            monitor.global_status(
                [self.check(monitor.OK), self.check(monitor.CRITICAL)]
            ),
            monitor.CRITICAL,
        )
        self.assertEqual(
            monitor.global_status(
                [self.check(monitor.OK), self.check(monitor.WARNING)]
            ),
            monitor.WARNING,
        )
        self.assertEqual(monitor.global_status([self.check(monitor.OK)]), monitor.OK)

    def test_primeiro_critical_envia_alerta(self):
        sender = mock.Mock(return_value=True)

        state, succeeded = monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            monitor.default_state(),
            FIXED_NOW,
            sender=sender,
        )

        sender.assert_called_once()
        self.assertEqual(sender.call_args.args[1], "ALERT")
        self.assertTrue(succeeded)
        self.assertEqual(state["notified_status"], monitor.CRITICAL)

    def test_critical_repetido_imediatamente_nao_envia_alerta(self):
        sender = mock.Mock(return_value=True)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "problem_checks": ["test_check"],
        }

        monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            previous_state,
            FIXED_NOW,
            sender=sender,
        )

        sender.assert_not_called()

    def test_critical_persistente_apos_intervalo_envia_lembrete(self):
        sender = mock.Mock(return_value=True)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(hours=7)).timestamp(),
            "problem_checks": ["test_check"],
        }

        monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            previous_state,
            FIXED_NOW,
            sender=sender,
        )

        sender.assert_called_once()
        self.assertEqual(sender.call_args.args[1], "REMINDER")

    def test_novo_check_critical_envia_alerta_com_global_inalterado(self):
        sender = mock.Mock(return_value=True)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "attempted_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "last_attempt_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "problem_checks": ["health_endpoint"],
        }
        results = [
            self.check(monitor.CRITICAL, "health_endpoint"),
            self.check(monitor.CRITICAL, "postgres_backup"),
        ]

        state, succeeded = monitor.process_alerts(
            self.config(), results, previous_state, FIXED_NOW, sender=sender
        )

        self.assertTrue(succeeded)
        sender.assert_called_once()
        self.assertEqual(sender.call_args.args[1], "ALERT")
        self.assertEqual(
            state["problem_checks"], ["health_endpoint", "postgres_backup"]
        )

    def test_mesma_lista_critical_nao_alerta_antes_do_repeat(self):
        sender = mock.Mock(return_value=True)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "attempted_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "last_attempt_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "problem_checks": ["health_endpoint", "postgres_backup"],
        }
        results = [
            self.check(monitor.CRITICAL, "health_endpoint"),
            self.check(monitor.CRITICAL, "postgres_backup"),
        ]

        state, succeeded = monitor.process_alerts(
            self.config(), results, previous_state, FIXED_NOW, sender=sender
        )

        self.assertTrue(succeeded)
        sender.assert_not_called()
        self.assertEqual(
            state["problem_checks"], ["health_endpoint", "postgres_backup"]
        )

    def test_novo_check_warning_envia_alerta_com_global_inalterado(self):
        sender = mock.Mock(return_value=True)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.WARNING,
            "notified_status": monitor.WARNING,
            "attempted_status": monitor.WARNING,
            "last_alert_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "last_attempt_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "problem_checks": ["disk_usage"],
        }
        results = [
            self.check(monitor.WARNING, "disk_usage"),
            self.check(monitor.WARNING, "monitor_state"),
        ]

        monitor.process_alerts(
            self.config(), results, previous_state, FIXED_NOW, sender=sender
        )

        sender.assert_called_once()
        self.assertEqual(sender.call_args.args[1], "ALERT")

    def test_novo_check_com_falha_smtp_nao_repete_a_cada_ciclo(self):
        sender = mock.Mock(return_value=False)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "attempted_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "last_attempt_epoch": (FIXED_NOW - timedelta(minutes=5)).timestamp(),
            "problem_checks": ["health_endpoint"],
        }
        results = [
            self.check(monitor.CRITICAL, "health_endpoint"),
            self.check(monitor.CRITICAL, "postgres_backup"),
        ]

        state, first_succeeded = monitor.process_alerts(
            self.config(), results, previous_state, FIXED_NOW, sender=sender
        )
        _, second_succeeded = monitor.process_alerts(
            self.config(),
            results,
            state,
            FIXED_NOW + timedelta(minutes=5),
            sender=sender,
        )

        self.assertFalse(first_succeeded)
        self.assertTrue(second_succeeded)
        self.assertEqual(sender.call_count, 1)
        self.assertEqual(
            state["problem_checks"], ["health_endpoint", "postgres_backup"]
        )

    def test_critical_para_ok_envia_recuperacao(self):
        sender = mock.Mock(return_value=True)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(hours=1)).timestamp(),
        }

        state, succeeded = monitor.process_alerts(
            self.config(),
            [self.check(monitor.OK)],
            previous_state,
            FIXED_NOW,
            sender=sender,
        )

        sender.assert_called_once()
        self.assertEqual(sender.call_args.args[1], "RECOVERY")
        self.assertTrue(succeeded)
        self.assertEqual(state["notified_status"], monitor.OK)

    def test_warning_e_alertado_sem_spam(self):
        sender = mock.Mock(return_value=True)

        state, _ = monitor.process_alerts(
            self.config(),
            [self.check(monitor.WARNING)],
            monitor.default_state(),
            FIXED_NOW,
            sender=sender,
        )
        monitor.process_alerts(
            self.config(),
            [self.check(monitor.WARNING)],
            state,
            FIXED_NOW + timedelta(minutes=5),
            sender=sender,
        )

        self.assertEqual(sender.call_count, 1)

    def test_falha_smtp_nao_e_retentada_antes_do_intervalo(self):
        sender = mock.Mock(return_value=False)

        state, first_succeeded = monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            monitor.default_state(),
            FIXED_NOW,
            sender=sender,
        )
        _, second_succeeded = monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            state,
            FIXED_NOW + timedelta(minutes=5),
            sender=sender,
        )

        self.assertFalse(first_succeeded)
        self.assertTrue(second_succeeded)
        self.assertEqual(sender.call_count, 1)
        self.assertEqual(state["notified_status"], monitor.OK)
        self.assertEqual(state["attempted_status"], monitor.CRITICAL)

    def test_falha_smtp_pode_ser_retentada_apos_intervalo(self):
        sender = mock.Mock(side_effect=[False, True])

        state, _ = monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            monitor.default_state(),
            FIXED_NOW,
            sender=sender,
        )
        recovered_state, succeeded = monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            state,
            FIXED_NOW + timedelta(hours=7),
            sender=sender,
        )

        self.assertTrue(succeeded)
        self.assertEqual(sender.call_count, 2)
        self.assertEqual(recovered_state["notified_status"], monitor.CRITICAL)

    def test_falha_de_lembrete_nao_e_retentada_a_cada_ciclo(self):
        sender = mock.Mock(return_value=False)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "attempted_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(hours=7)).timestamp(),
            "last_attempt_epoch": (FIXED_NOW - timedelta(hours=7)).timestamp(),
            "problem_checks": ["test_check"],
        }

        state, _ = monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            previous_state,
            FIXED_NOW,
            sender=sender,
        )
        monitor.process_alerts(
            self.config(),
            [self.check(monitor.CRITICAL)],
            state,
            FIXED_NOW + timedelta(minutes=5),
            sender=sender,
        )

        self.assertEqual(sender.call_count, 1)

    def test_falha_de_recuperacao_nao_e_retentada_a_cada_ciclo(self):
        sender = mock.Mock(return_value=False)
        previous_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
            "notified_status": monitor.CRITICAL,
            "attempted_status": monitor.CRITICAL,
            "last_alert_epoch": (FIXED_NOW - timedelta(hours=1)).timestamp(),
            "last_attempt_epoch": (FIXED_NOW - timedelta(hours=1)).timestamp(),
        }

        state, _ = monitor.process_alerts(
            self.config(),
            [self.check(monitor.OK)],
            previous_state,
            FIXED_NOW,
            sender=sender,
        )
        monitor.process_alerts(
            self.config(),
            [self.check(monitor.OK)],
            state,
            FIXED_NOW + timedelta(minutes=5),
            sender=sender,
        )

        self.assertEqual(sender.call_count, 1)

    def test_envio_smtp_usa_tls_login_e_email_message(self):
        smtp = mock.MagicMock()
        smtp_factory = mock.MagicMock()
        smtp_factory.return_value.__enter__.return_value = smtp

        succeeded = monitor.send_notification(
            self.config(),
            "ALERT",
            [self.check(monitor.CRITICAL)],
            FIXED_NOW,
            smtp_factory=smtp_factory,
        )

        self.assertTrue(succeeded)
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with(
            "monitor@example.invalid", "smtp-test-password"
        )
        smtp.send_message.assert_called_once()
        method_names = [call[0] for call in smtp.method_calls]
        self.assertLess(method_names.index("starttls"), method_names.index("login"))

    def test_falha_smtp_e_sanitizada_sem_senha(self):
        stderr = StringIO()

        with redirect_stderr(stderr):
            succeeded = monitor.send_notification(
                self.config(),
                "ALERT",
                [self.check(monitor.CRITICAL)],
                FIXED_NOW,
                smtp_factory=mock.Mock(
                    side_effect=smtplib.SMTPException("smtp-test-password")
                ),
            )

        self.assertFalse(succeeded)
        self.assertIn("SMTP_ALERT_FAILED", stderr.getvalue())
        self.assertNotIn("smtp-test-password", stderr.getvalue())

    def test_falha_starttls_e_sanitizada_e_impede_login(self):
        smtp = mock.MagicMock()
        smtp.starttls.side_effect = ssl.SSLError("smtp-test-password")
        smtp_factory = mock.MagicMock()
        smtp_factory.return_value.__enter__.return_value = smtp
        stderr = StringIO()

        with redirect_stderr(stderr):
            succeeded = monitor.send_notification(
                self.config(),
                "ALERT",
                [self.check(monitor.CRITICAL)],
                FIXED_NOW,
                smtp_factory=smtp_factory,
            )

        self.assertFalse(succeeded)
        smtp.login.assert_not_called()
        self.assertEqual(stderr.getvalue().strip(), "[monitor] SMTP_ALERT_FAILED")
        self.assertNotIn("smtp-test-password", stderr.getvalue())

    def test_state_file_inexistente_retorna_estado_inicial(self):
        state, warning = monitor.load_state(self.base_path / "inexistente.json")

        self.assertEqual(state, monitor.default_state())
        self.assertIsNone(warning)

    def test_state_file_corrompido_e_tratado_com_seguranca(self):
        state_path = self.base_path / "state.json"
        state_path.write_text("{conteúdo inválido", encoding="utf-8")

        state, warning = monitor.load_state(state_path)

        self.assertEqual(state, monitor.default_state())
        self.assertIn("inválido", warning)

    def test_state_file_atomico_restrito_e_sem_secrets(self):
        state_path = self.base_path / "state" / "monitor-state.json"
        state = {
            **monitor.default_state(),
            "problem_checks": ["health_endpoint"],
        }

        monitor.save_state(state_path, state)

        content = state_path.read_text(encoding="utf-8")
        self.assertNotIn("smtp-test-password", content)
        self.assertNotIn("DATABASE_URL", content)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(state_path.stat().st_mode), 0o600)
        self.assertEqual(monitor.load_state(state_path)[0], state)

    def test_execucao_saudavel_retorna_exit_zero(self):
        with (
            mock.patch.object(
                monitor.MonitorConfig, "from_environment", return_value=self.config()
            ),
            mock.patch.object(
                monitor, "load_state", return_value=(monitor.default_state(), None)
            ),
            mock.patch.object(
                monitor, "run_all_checks", return_value=[self.check(monitor.OK)]
            ),
            mock.patch.object(
                monitor,
                "process_alerts",
                return_value=(monitor.default_state(), True),
            ),
            mock.patch.object(monitor, "save_state"),
            redirect_stdout(StringIO()),
        ):
            exit_code = monitor.main({})

        self.assertEqual(exit_code, monitor.EXIT_OK)

    def test_execucao_com_falha_retorna_exit_um(self):
        critical_state = {
            **monitor.default_state(),
            "observed_status": monitor.CRITICAL,
        }
        with (
            mock.patch.object(
                monitor.MonitorConfig, "from_environment", return_value=self.config()
            ),
            mock.patch.object(
                monitor, "load_state", return_value=(monitor.default_state(), None)
            ),
            mock.patch.object(
                monitor,
                "run_all_checks",
                return_value=[self.check(monitor.CRITICAL)],
            ),
            mock.patch.object(
                monitor, "process_alerts", return_value=(critical_state, True)
            ),
            mock.patch.object(monitor, "save_state"),
            redirect_stdout(StringIO()),
        ):
            exit_code = monitor.main({})

        self.assertEqual(exit_code, monitor.EXIT_OPERATIONAL_FAILURE)

    def test_erro_de_configuracao_retorna_exit_dois_sem_traceback(self):
        stderr = StringIO()

        with redirect_stderr(stderr):
            exit_code = monitor.main({})

        self.assertEqual(exit_code, monitor.EXIT_CONFIGURATION_ERROR)
        self.assertIn("CONFIG_ERROR", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_database_url_nao_aparece_nos_logs(self):
        secret_uri = "postgresql://usuario:senha-secreta@host-interno/banco"
        environment = self.valid_environment()
        environment["DATABASE_URL"] = secret_uri

        with (
            mock.patch.object(
                monitor,
                "run_all_checks",
                return_value=[self.check(monitor.CRITICAL, "health_endpoint")],
            ),
            mock.patch.object(
                monitor, "load_state", return_value=(monitor.default_state(), None)
            ),
            mock.patch.object(
                monitor,
                "process_alerts",
                return_value=(monitor.default_state(), True),
            ),
            mock.patch.object(monitor, "save_state"),
            redirect_stdout(StringIO()) as stdout,
            redirect_stderr(StringIO()) as stderr,
        ):
            monitor.main(environment)

        output = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn(secret_uri, output)
        self.assertNotIn("senha-secreta", output)

    def test_falha_de_escrita_do_state_retorna_exit_dois(self):
        with (
            mock.patch.object(
                monitor.MonitorConfig, "from_environment", return_value=self.config()
            ),
            mock.patch.object(
                monitor, "load_state", return_value=(monitor.default_state(), None)
            ),
            mock.patch.object(
                monitor, "run_all_checks", return_value=[self.check(monitor.OK)]
            ),
            mock.patch.object(
                monitor,
                "process_alerts",
                return_value=(monitor.default_state(), True),
            ),
            mock.patch.object(monitor, "save_state", side_effect=OSError),
            redirect_stdout(StringIO()),
            redirect_stderr(StringIO()),
        ):
            exit_code = monitor.main({})

        self.assertEqual(exit_code, monitor.EXIT_CONFIGURATION_ERROR)

    def test_checks_sao_independentes_quando_um_lanca_excecao(self):
        ok = self.check(monitor.OK)
        with (
            mock.patch.object(
                monitor,
                "check_systemd_service",
                side_effect=[RuntimeError("detalhe interno"), ok],
            ),
            mock.patch.object(monitor, "check_health_endpoint", return_value=ok),
            mock.patch.object(monitor, "check_systemd_timer", return_value=ok),
            mock.patch.object(monitor, "check_latest_backup", return_value=ok),
            mock.patch.object(monitor, "check_oneshot_result", return_value=ok),
            mock.patch.object(monitor, "check_disk_usage", return_value=ok),
        ):
            results = monitor.run_all_checks(self.config(), now=FIXED_NOW)

        self.assertEqual(len(results), 10)
        self.assertEqual(results[0].status, monitor.CRITICAL)
        self.assertEqual(results[0].message, "check falhou internamente")
        self.assertTrue(all(result.status == monitor.OK for result in results[1:]))

    def test_unit_service_aplica_usuario_ambiente_e_hardening(self):
        service = (
            Path(settings.BASE_DIR)
            / "ops"
            / "systemd"
            / "justica-monitor.service"
        ).read_text(encoding="utf-8")

        for expected in (
            "User=deploy",
            "Group=deploy",
            "EnvironmentFile=/etc/justica-climatica/monitoring.env",
            "ExecStart=/usr/bin/python3 /srv/justica-climatica/ops/monitor.py",
            "NoNewPrivileges=true",
            "PrivateTmp=true",
            "ProtectHome=true",
            "ProtectSystem=strict",
            "ReadOnlyPaths=/srv/justica-climatica/backups",
            "ReadWritePaths=/srv/justica-climatica/ops-state",
            "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, service)

        self.assertNotIn("User=root", service)

    def test_unit_timer_aponta_para_service_e_intervalo_de_cinco_minutos(self):
        timer = (
            Path(settings.BASE_DIR)
            / "ops"
            / "systemd"
            / "justica-monitor.timer"
        ).read_text(encoding="utf-8")

        self.assertIn("OnUnitActiveSec=5min", timer)
        self.assertIn("Unit=justica-monitor.service", timer)
        self.assertIn("WantedBy=timers.target", timer)
