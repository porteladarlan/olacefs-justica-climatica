#!/usr/bin/env python3
"""Monitoramento operacional independente da aplicação Django."""

from __future__ import annotations

import json
import os
import re
import shutil
import smtplib
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
from typing import Callable, Mapping, Sequence
from urllib.parse import urlsplit


OK = "OK"
WARNING = "WARNING"
CRITICAL = "CRITICAL"
VALID_STATUSES = {OK, WARNING, CRITICAL}

EXIT_OK = 0
EXIT_OPERATIONAL_FAILURE = 1
EXIT_CONFIGURATION_ERROR = 2

SYSTEMCTL_BIN = "/usr/bin/systemctl"
POSTGRES_BACKUP_PATTERN = re.compile(
    r"^justica-climatica-(?P<timestamp>\d{8}T\d{6}Z)\.dump$"
)
MEDIA_BACKUP_PATTERN = re.compile(
    r"^justica-climatica-media-(?P<timestamp>\d{8}T\d{6}Z)\.tar\.gz$"
)
STATE_VERSION = 1
MAX_STATE_FILE_BYTES = 65_536
BACKUP_FUTURE_TOLERANCE_SECONDS = 300


class ConfigurationError(ValueError):
    """Erro de configuração que pode ser exibido sem revelar valores sensíveis."""


@dataclass(frozen=True)
class CheckResult:
    check: str
    status: str
    message: str
    timestamp: str


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str


@dataclass(frozen=True)
class MonitorConfig:
    environment: str
    health_url: str
    alert_recipients: tuple[str, ...]
    smtp_host: str
    smtp_port: int
    smtp_use_tls: bool
    smtp_user: str
    smtp_password: str
    from_email: str
    timeout_seconds: int
    backup_max_age_seconds: int
    disk_warning_percent: float
    disk_critical_percent: float
    alert_repeat_seconds: int
    state_file: Path
    postgres_backup_dir: Path
    media_backup_dir: Path
    disk_path: Path

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> "MonitorConfig":
        monitor_environment = environment.get("MONITOR_ENVIRONMENT", "staging").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", monitor_environment):
            raise ConfigurationError("MONITOR_ENVIRONMENT possui formato inválido.")

        health_url = environment.get(
            "MONITOR_HEALTH_URL",
            "https://olacefs-justiciaclimatica.gizapps.org.br/health/",
        ).strip()
        parsed_health_url = urlsplit(health_url)
        if (
            parsed_health_url.scheme != "https"
            or not parsed_health_url.hostname
            or parsed_health_url.username is not None
            or parsed_health_url.password is not None
        ):
            raise ConfigurationError(
                "MONITOR_HEALTH_URL deve ser HTTPS e não pode conter credenciais."
            )

        recipients = tuple(
            address.strip()
            for address in environment.get("MONITOR_ALERT_RECIPIENTS", "").split(",")
            if address.strip()
        )
        if not recipients:
            raise ConfigurationError("MONITOR_ALERT_RECIPIENTS não está configurado.")
        for recipient in recipients:
            _validate_email_address(recipient, "MONITOR_ALERT_RECIPIENTS")

        smtp_host = _required_value(environment, "MONITOR_SMTP_HOST")
        if any(character in smtp_host for character in "\r\n"):
            raise ConfigurationError("MONITOR_SMTP_HOST possui formato inválido.")
        smtp_user = _required_value(environment, "MONITOR_SMTP_USER")
        smtp_password = _required_value(environment, "MONITOR_SMTP_PASSWORD")
        from_email = _required_value(environment, "MONITOR_FROM_EMAIL")
        _validate_email_address(from_email, "MONITOR_FROM_EMAIL")

        smtp_port = _positive_integer(environment, "MONITOR_SMTP_PORT", 587)
        timeout_seconds = _positive_integer(
            environment, "MONITOR_TIMEOUT_SECONDS", 10
        )
        backup_max_age_seconds = _positive_integer(
            environment, "MONITOR_BACKUP_MAX_AGE_SECONDS", 129_600
        )
        alert_repeat_seconds = _positive_integer(
            environment, "MONITOR_ALERT_REPEAT_SECONDS", 21_600
        )
        smtp_use_tls = _boolean_value(
            environment, "MONITOR_SMTP_USE_TLS", default=True
        )
        if not smtp_use_tls:
            raise ConfigurationError(
                "MONITOR_SMTP_USE_TLS deve permanecer habilitado."
            )
        disk_warning_percent = _percentage_value(
            environment, "MONITOR_DISK_WARNING_PERCENT", 80
        )
        disk_critical_percent = _percentage_value(
            environment, "MONITOR_DISK_CRITICAL_PERCENT", 90
        )
        if not 0 < disk_warning_percent < disk_critical_percent <= 100:
            raise ConfigurationError(
                "Thresholds de disco devem satisfazer 0 < warning < critical <= 100."
            )

        return cls(
            environment=monitor_environment,
            health_url=health_url,
            alert_recipients=recipients,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_use_tls=smtp_use_tls,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_email=from_email,
            timeout_seconds=timeout_seconds,
            backup_max_age_seconds=backup_max_age_seconds,
            disk_warning_percent=disk_warning_percent,
            disk_critical_percent=disk_critical_percent,
            alert_repeat_seconds=alert_repeat_seconds,
            state_file=_absolute_path(
                environment,
                "MONITOR_STATE_FILE",
                "/srv/justica-climatica/ops-state/monitor-state.json",
            ),
            postgres_backup_dir=_absolute_path(
                environment,
                "MONITOR_POSTGRES_BACKUP_DIR",
                "/srv/justica-climatica/backups/postgres",
            ),
            media_backup_dir=_absolute_path(
                environment,
                "MONITOR_MEDIA_BACKUP_DIR",
                "/srv/justica-climatica/backups/media",
            ),
            disk_path=_absolute_path(
                environment,
                "MONITOR_DISK_PATH",
                "/srv/justica-climatica",
            ),
        )


def _required_value(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} não está configurado.")
    return value


def _positive_integer(
    environment: Mapping[str, str], name: str, default: int
) -> int:
    raw_value = environment.get(name, str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} deve ser inteiro positivo.") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} deve ser inteiro positivo.")
    return value


def _percentage_value(
    environment: Mapping[str, str], name: str, default: float
) -> float:
    raw_value = environment.get(name, str(default)).strip()
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} deve ser percentual numérico.") from exc


def _boolean_value(
    environment: Mapping[str, str], name: str, *, default: bool
) -> bool:
    raw_value = environment.get(name, str(default)).strip().lower()
    if raw_value in {"1", "true", "yes", "on"}:
        return True
    if raw_value in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} deve ser booleano explícito.")


def _absolute_path(
    environment: Mapping[str, str], name: str, default: str
) -> Path:
    path = Path(environment.get(name, default).strip())
    if not path.is_absolute():
        raise ConfigurationError(f"{name} deve ser caminho absoluto.")
    return path


def _validate_email_address(address: str, variable_name: str) -> None:
    parsed_name, parsed_address = parseaddr(address)
    if (
        parsed_name
        or parsed_address != address
        or "@" not in parsed_address
        or any(character in address for character in "\r\n")
    ):
        raise ConfigurationError(f"{variable_name} contém endereço inválido.")


def utc_now() -> datetime:
    return datetime.now(UTC)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def result(
    check: str, status: str, message: str, *, now: datetime | None = None
) -> CheckResult:
    return CheckResult(
        check=check,
        status=status,
        message=message,
        timestamp=format_timestamp(now or utc_now()),
    )


def run_command(arguments: Sequence[str], timeout: int) -> CommandResult | None:
    try:
        completed = subprocess.run(
            list(arguments),
            check=False,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return CommandResult(returncode=completed.returncode, stdout=completed.stdout)


def _parse_systemd_properties(output: str) -> dict[str, str]:
    properties: dict[str, str] = {}
    for line in output.splitlines():
        name, separator, value = line.partition("=")
        if separator:
            properties[name] = value.strip()
    return properties


def check_systemd_service(
    check_id: str,
    unit: str,
    timeout: int,
    *,
    command_runner: Callable[[Sequence[str], int], CommandResult | None] = run_command,
    now: datetime | None = None,
) -> CheckResult:
    command_result = command_runner(
        [
            SYSTEMCTL_BIN,
            "show",
            unit,
            "--no-page",
            "--property=LoadState",
            "--property=ActiveState",
            "--property=SubState",
        ],
        timeout,
    )
    if command_result is None or command_result.returncode != 0:
        return result(check_id, CRITICAL, "não foi possível consultar o serviço", now=now)
    properties = _parse_systemd_properties(command_result.stdout)
    if properties.get("LoadState") != "loaded":
        return result(check_id, CRITICAL, "serviço não está carregado", now=now)
    if properties.get("ActiveState") != "active":
        return result(check_id, CRITICAL, "serviço não está active", now=now)
    return result(check_id, OK, "serviço active", now=now)


def check_systemd_timer(
    check_id: str,
    unit: str,
    timeout: int,
    *,
    command_runner: Callable[[Sequence[str], int], CommandResult | None] = run_command,
    now: datetime | None = None,
) -> CheckResult:
    enabled = command_runner([SYSTEMCTL_BIN, "is-enabled", unit], timeout)
    if enabled is None or enabled.returncode != 0 or enabled.stdout.strip() != "enabled":
        return result(check_id, CRITICAL, "timer não está enabled", now=now)

    active = command_runner([SYSTEMCTL_BIN, "is-active", unit], timeout)
    if active is None or active.returncode != 0 or active.stdout.strip() != "active":
        return result(check_id, CRITICAL, "timer não está active", now=now)

    schedule = command_runner(
        [
            SYSTEMCTL_BIN,
            "show",
            unit,
            "--no-page",
            "--property=NextElapseUSecRealtime",
            "--value",
        ],
        timeout,
    )
    if schedule and schedule.returncode == 0 and schedule.stdout.strip():
        message = "timer enabled, active e com próxima execução agendada"
    else:
        message = "timer enabled e active"
    return result(check_id, OK, message, now=now)


def check_oneshot_result(
    check_id: str,
    unit: str,
    timeout: int,
    *,
    command_runner: Callable[[Sequence[str], int], CommandResult | None] = run_command,
    now: datetime | None = None,
) -> CheckResult:
    command_result = command_runner(
        [
            SYSTEMCTL_BIN,
            "show",
            unit,
            "--no-page",
            "--property=LoadState",
            "--property=ActiveState",
            "--property=Result",
        ],
        timeout,
    )
    if command_result is None or command_result.returncode != 0:
        return result(check_id, CRITICAL, "não foi possível consultar o backup", now=now)
    properties = _parse_systemd_properties(command_result.stdout)
    if properties.get("LoadState") != "loaded":
        return result(check_id, CRITICAL, "service de backup não está carregado", now=now)
    if properties.get("Result", "") not in {"", "success"}:
        return result(check_id, CRITICAL, "último resultado do backup falhou", now=now)
    return result(check_id, OK, "último resultado do backup foi success", now=now)


def check_health_endpoint(
    url: str,
    timeout: int,
    *,
    opener: Callable[..., object] = urllib.request.urlopen,
    now: datetime | None = None,
) -> CheckResult:
    try:
        with opener(url, timeout=timeout) as response:
            status_code = response.getcode()
    except urllib.error.HTTPError as exc:
        return result(
            "health_endpoint",
            CRITICAL,
            f"health endpoint retornou HTTP {exc.code}",
            now=now,
        )
    except (OSError, TimeoutError, ssl.SSLError, urllib.error.URLError, ValueError):
        return result(
            "health_endpoint", CRITICAL, "health endpoint indisponível", now=now
        )
    if status_code != 200:
        return result(
            "health_endpoint",
            CRITICAL,
            f"health endpoint retornou HTTP {status_code}",
            now=now,
        )
    return result("health_endpoint", OK, "HTTP 200", now=now)


def _backup_timestamp(match: re.Match[str]) -> datetime:
    return datetime.strptime(match.group("timestamp"), "%Y%m%dT%H%M%SZ").replace(
        tzinfo=UTC
    )


def check_latest_backup(
    check_id: str,
    directory: Path,
    filename_pattern: re.Pattern[str],
    max_age_seconds: int,
    *,
    now: datetime | None = None,
) -> CheckResult:
    current_time = now or utc_now()
    try:
        candidates: list[tuple[datetime, Path]] = []
        for entry in directory.iterdir():
            match = filename_pattern.fullmatch(entry.name)
            if match and entry.is_file() and not entry.is_symlink():
                candidates.append((_backup_timestamp(match), entry))
    except (OSError, ValueError):
        return result(check_id, CRITICAL, "diretório de backup indisponível", now=current_time)

    if not candidates:
        return result(check_id, CRITICAL, "nenhum backup válido encontrado", now=current_time)

    backup_time, backup_path = max(candidates, key=lambda candidate: candidate[0])
    try:
        if backup_path.stat().st_size <= 0:
            return result(check_id, CRITICAL, "último backup está vazio", now=current_time)
        checksum_path = Path(f"{backup_path}.sha256")
        if (
            not checksum_path.is_file()
            or checksum_path.is_symlink()
            or checksum_path.stat().st_size <= 0
        ):
            return result(
                check_id, CRITICAL, "checksum do último backup está ausente", now=current_time
            )
    except OSError:
        return result(check_id, CRITICAL, "último backup não pôde ser validado", now=current_time)

    if backup_time > current_time + timedelta(
        seconds=BACKUP_FUTURE_TOLERANCE_SECONDS
    ):
        return result(
            check_id,
            CRITICAL,
            "timestamp do último backup está no futuro",
            now=current_time,
        )

    age_seconds = max(0, int((current_time - backup_time).total_seconds()))
    if age_seconds > max_age_seconds:
        return result(check_id, CRITICAL, "último backup está atrasado", now=current_time)
    return result(check_id, OK, "último backup está recente", now=current_time)


def check_disk_usage(
    path: Path,
    warning_percent: float,
    critical_percent: float,
    *,
    disk_usage: Callable[[Path], object] = shutil.disk_usage,
    now: datetime | None = None,
) -> CheckResult:
    try:
        usage = disk_usage(path)
        used_percent = (usage.used / usage.total) * 100
    except (OSError, ZeroDivisionError):
        return result("disk_usage", CRITICAL, "uso de disco indisponível", now=now)
    if used_percent >= critical_percent:
        status = CRITICAL
    elif used_percent >= warning_percent:
        status = WARNING
    else:
        status = OK
    return result(
        "disk_usage",
        status,
        f"uso de disco {used_percent:.1f}%",
        now=now,
    )


def run_all_checks(
    config: MonitorConfig, *, now: datetime | None = None
) -> list[CheckResult]:
    current_time = now or utc_now()
    checks: tuple[tuple[str, Callable[[], CheckResult]], ...] = (
        (
            "django_service",
            lambda: check_systemd_service(
                "django_service",
                "justica-climatica.service",
                config.timeout_seconds,
                now=current_time,
            ),
        ),
        (
            "nginx_service",
            lambda: check_systemd_service(
                "nginx_service",
                "nginx.service",
                config.timeout_seconds,
                now=current_time,
            ),
        ),
        (
            "health_endpoint",
            lambda: check_health_endpoint(
                config.health_url, config.timeout_seconds, now=current_time
            ),
        ),
        (
            "postgres_timer",
            lambda: check_systemd_timer(
                "postgres_timer",
                "justica-backup-postgres.timer",
                config.timeout_seconds,
                now=current_time,
            ),
        ),
        (
            "media_timer",
            lambda: check_systemd_timer(
                "media_timer",
                "justica-backup-media.timer",
                config.timeout_seconds,
                now=current_time,
            ),
        ),
        (
            "postgres_backup",
            lambda: check_latest_backup(
                "postgres_backup",
                config.postgres_backup_dir,
                POSTGRES_BACKUP_PATTERN,
                config.backup_max_age_seconds,
                now=current_time,
            ),
        ),
        (
            "media_backup",
            lambda: check_latest_backup(
                "media_backup",
                config.media_backup_dir,
                MEDIA_BACKUP_PATTERN,
                config.backup_max_age_seconds,
                now=current_time,
            ),
        ),
        (
            "postgres_backup_service",
            lambda: check_oneshot_result(
                "postgres_backup_service",
                "justica-backup-postgres.service",
                config.timeout_seconds,
                now=current_time,
            ),
        ),
        (
            "media_backup_service",
            lambda: check_oneshot_result(
                "media_backup_service",
                "justica-backup-media.service",
                config.timeout_seconds,
                now=current_time,
            ),
        ),
        (
            "disk_usage",
            lambda: check_disk_usage(
                config.disk_path,
                config.disk_warning_percent,
                config.disk_critical_percent,
                now=current_time,
            ),
        ),
    )

    check_results: list[CheckResult] = []
    for check_id, check in checks:
        try:
            check_results.append(check())
        except Exception:
            check_results.append(
                result(
                    check_id,
                    CRITICAL,
                    "check falhou internamente",
                    now=current_time,
                )
            )
    return check_results


def global_status(results: Sequence[CheckResult]) -> str:
    statuses = {check.status for check in results}
    if CRITICAL in statuses:
        return CRITICAL
    if WARNING in statuses:
        return WARNING
    return OK


def default_state() -> dict[str, object]:
    return {
        "version": STATE_VERSION,
        "observed_status": OK,
        "notified_status": OK,
        "last_alert_epoch": None,
        "attempted_status": OK,
        "last_attempt_epoch": None,
        "problem_checks": [],
    }


def load_state(path: Path) -> tuple[dict[str, object], str | None]:
    if not path.exists():
        return default_state(), None
    try:
        if path.is_symlink() or path.stat().st_size > MAX_STATE_FILE_BYTES:
            raise ValueError
        with path.open("r", encoding="utf-8") as state_file:
            raw_state = json.load(state_file)
        if not isinstance(raw_state, dict):
            raise ValueError
        observed_status = raw_state.get("observed_status")
        notified_status = raw_state.get("notified_status")
        last_alert_epoch = raw_state.get("last_alert_epoch")
        attempted_status = raw_state.get("attempted_status", notified_status)
        last_attempt_epoch = raw_state.get("last_attempt_epoch", last_alert_epoch)
        problem_checks = raw_state.get("problem_checks")
        if (
            observed_status not in VALID_STATUSES
            or notified_status not in VALID_STATUSES
            or attempted_status not in VALID_STATUSES
        ):
            raise ValueError
        if last_alert_epoch is not None and not isinstance(last_alert_epoch, (int, float)):
            raise ValueError
        if last_attempt_epoch is not None and not isinstance(
            last_attempt_epoch, (int, float)
        ):
            raise ValueError
        if not isinstance(problem_checks, list) or not all(
            isinstance(check, str) for check in problem_checks
        ):
            raise ValueError
    except (OSError, ValueError, json.JSONDecodeError):
        return default_state(), "state file inválido; estado seguro reconstruído"

    return {
        "version": STATE_VERSION,
        "observed_status": observed_status,
        "notified_status": notified_status,
        "last_alert_epoch": last_alert_epoch,
        "attempted_status": attempted_status,
        "last_attempt_epoch": last_attempt_epoch,
        "problem_checks": problem_checks,
    }, None


def save_state(path: Path, state: Mapping[str, object]) -> None:
    state_directory = path.parent
    state_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if state_directory.is_symlink() or path.is_symlink():
        raise OSError("state path inseguro")

    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=".monitor-state-", suffix=".tmp", dir=state_directory
    )
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(file_descriptor, 0o600)
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as state_file:
            json.dump(state, state_file, sort_keys=True, separators=(",", ":"))
            state_file.write("\n")
            state_file.flush()
            os.fsync(state_file.fileno())
        os.replace(temporary_path, path)
        os.chmod(path, 0o600)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _notification_subject(config: MonitorConfig, notification_type: str) -> str:
    label = "RECUPERADO" if notification_type == "RECOVERY" else "ALERTA OPERACIONAL"
    return f"[Justiça Climática][{config.environment.upper()}] {label}"


def _notification_body(
    config: MonitorConfig,
    notification_type: str,
    results: Sequence[CheckResult],
    now: datetime,
) -> str:
    current_status = global_status(results)
    lines = [
        f"Ambiente: {config.environment}",
        f"Horário UTC: {format_timestamp(now)}",
        f"Estado atual: {current_status}",
    ]
    if notification_type == "RECOVERY":
        lines.append("Checks recuperados: todos os checks operacionais estão OK.")
    else:
        lines.append("Checks com problema:")
        for check in results:
            if check.status != OK:
                lines.append(f"- {check.check}: {check.status} — {check.message}")
    lines.append("Consulte o journald da unit justica-monitor.service.")
    return "\n".join(lines)


def send_notification(
    config: MonitorConfig,
    notification_type: str,
    results: Sequence[CheckResult],
    now: datetime,
    *,
    smtp_factory: Callable[..., object] = smtplib.SMTP,
) -> bool:
    message = EmailMessage()
    message["Subject"] = _notification_subject(config, notification_type)
    message["From"] = config.from_email
    message["To"] = ", ".join(config.alert_recipients)
    message.set_content(_notification_body(config, notification_type, results, now))

    try:
        with smtp_factory(
            config.smtp_host, config.smtp_port, timeout=config.timeout_seconds
        ) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(config.smtp_user, config.smtp_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException, ssl.SSLError):
        print("[monitor] SMTP_ALERT_FAILED", file=sys.stderr)
        return False
    return True


def process_alerts(
    config: MonitorConfig,
    results: Sequence[CheckResult],
    previous_state: Mapping[str, object],
    now: datetime,
    *,
    sender: Callable[[MonitorConfig, str, Sequence[CheckResult], datetime], bool] = send_notification,
) -> tuple[dict[str, object], bool]:
    current_status = global_status(results)
    notified_status = str(previous_state.get("notified_status", OK))
    last_alert_epoch = previous_state.get("last_alert_epoch")
    attempted_status = str(previous_state.get("attempted_status", notified_status))
    last_attempt_epoch = previous_state.get("last_attempt_epoch", last_alert_epoch)
    previous_problem_checks = {
        str(check) for check in previous_state.get("problem_checks", [])
    }
    current_problem_checks = {
        check.check for check in results if check.status != OK
    }
    new_problem_checks = current_problem_checks - previous_problem_checks
    current_epoch = now.timestamp()
    notification_type: str | None = None

    if current_status != OK:
        if new_problem_checks:
            notification_type = "ALERT"
        elif notified_status == OK or notified_status != current_status:
            if (
                attempted_status != current_status
                or not isinstance(last_attempt_epoch, (int, float))
                or current_epoch - last_attempt_epoch >= config.alert_repeat_seconds
            ):
                notification_type = "ALERT"
        else:
            repeat_reference = last_alert_epoch
            if (
                attempted_status == current_status
                and isinstance(last_attempt_epoch, (int, float))
                and (
                    not isinstance(repeat_reference, (int, float))
                    or last_attempt_epoch > repeat_reference
                )
            ):
                repeat_reference = last_attempt_epoch
            if (
                isinstance(repeat_reference, (int, float))
                and current_epoch - repeat_reference >= config.alert_repeat_seconds
            ):
                notification_type = "REMINDER"
    elif notified_status != OK and (
        attempted_status != OK
        or not isinstance(last_attempt_epoch, (int, float))
        or current_epoch - last_attempt_epoch >= config.alert_repeat_seconds
    ):
        notification_type = "RECOVERY"

    notification_succeeded = True
    new_notified_status = notified_status
    new_last_alert_epoch = last_alert_epoch
    new_attempted_status = attempted_status
    new_last_attempt_epoch = last_attempt_epoch
    if notification_type is not None:
        notification_succeeded = sender(config, notification_type, results, now)
        new_attempted_status = current_status
        new_last_attempt_epoch = current_epoch
        if notification_succeeded:
            new_notified_status = current_status
            new_last_alert_epoch = current_epoch

    new_state: dict[str, object] = {
        "version": STATE_VERSION,
        "observed_status": current_status,
        "notified_status": new_notified_status,
        "last_alert_epoch": new_last_alert_epoch,
        "attempted_status": new_attempted_status,
        "last_attempt_epoch": new_last_attempt_epoch,
        "problem_checks": sorted(current_problem_checks),
    }
    return new_state, notification_succeeded


def _log_results(results: Sequence[CheckResult]) -> None:
    status = global_status(results)
    problems = [check.check for check in results if check.status != OK]
    if problems:
        print(
            f"[monitor] STATUS={status} checks={len(results)} "
            f"failures={','.join(problems)}"
        )
        for check in results:
            if check.status != OK:
                print(
                    f"[monitor] check={check.check} status={check.status} "
                    f"message={check.message} timestamp={check.timestamp}"
                )
    else:
        print(f"[monitor] STATUS=OK checks={len(results)}")


def main(environment: Mapping[str, str] | None = None) -> int:
    os.umask(0o077)
    source_environment = os.environ if environment is None else environment
    try:
        config = MonitorConfig.from_environment(source_environment)
    except ConfigurationError as exc:
        print(f"[monitor] CONFIG_ERROR: {exc}", file=sys.stderr)
        return EXIT_CONFIGURATION_ERROR

    current_time = utc_now()
    previous_state, state_warning = load_state(config.state_file)
    results = run_all_checks(config, now=current_time)
    if state_warning:
        results.append(
            result("monitor_state", WARNING, state_warning, now=current_time)
        )

    _log_results(results)
    new_state, notification_succeeded = process_alerts(
        config, results, previous_state, current_time
    )
    try:
        save_state(config.state_file, new_state)
    except OSError:
        print("[monitor] STATE_WRITE_FAILED", file=sys.stderr)
        return EXIT_CONFIGURATION_ERROR

    if global_status(results) != OK or not notification_succeeded:
        return EXIT_OPERATIONAL_FAILURE
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
