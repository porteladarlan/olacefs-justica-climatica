#!/usr/bin/env python3
"""Execute clientes PostgreSQL com conexão libpq derivada de DATABASE_URL."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from urllib.parse import parse_qsl, unquote, urlsplit


QUERY_PARAMETER_ENV = {
    "sslmode": "PGSSLMODE",
    "sslrootcert": "PGSSLROOTCERT",
    "sslcert": "PGSSLCERT",
    "sslkey": "PGSSLKEY",
    "connect_timeout": "PGCONNECT_TIMEOUT",
    "application_name": "PGAPPNAME",
    "target_session_attrs": "PGTARGETSESSIONATTRS",
}
INVALID_PERCENT_ENCODING = re.compile(r"%(?![0-9A-Fa-f]{2})")


class ConfigurationError(ValueError):
    """Indica configuração de conexão inválida sem carregar dados sensíveis."""


def _decode_component(value: str, field_name: str) -> str:
    if INVALID_PERCENT_ENCODING.search(value):
        raise ConfigurationError(
            f"Percent-encoding inválido no campo {field_name} da DATABASE_URL."
        )
    try:
        decoded = unquote(value, encoding="utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ConfigurationError(
            f"Codificação inválida no campo {field_name} da DATABASE_URL."
        ) from exc
    if "\x00" in decoded:
        raise ConfigurationError(
            f"Caractere inválido no campo {field_name} da DATABASE_URL."
        )
    return decoded


def parse_database_url(database_url: str) -> dict[str, str]:
    """Converta uma URI PostgreSQL validada em variáveis de ambiente libpq."""

    try:
        parsed = urlsplit(database_url)
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("DATABASE_URL inválida.") from exc

    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ConfigurationError("DATABASE_URL deve usar postgresql:// ou postgres://.")
    if parsed.fragment:
        raise ConfigurationError("DATABASE_URL não pode conter fragmento.")
    if not parsed.hostname:
        raise ConfigurationError("DATABASE_URL deve informar o host.")
    if parsed.username is None:
        raise ConfigurationError("DATABASE_URL deve informar o usuário.")
    if parsed.password is None:
        raise ConfigurationError("DATABASE_URL deve informar a senha.")
    if not parsed.path.startswith("/") or len(parsed.path) == 1:
        raise ConfigurationError("DATABASE_URL deve informar o nome do banco.")

    raw_database = parsed.path[1:]
    if "/" in raw_database:
        raise ConfigurationError("DATABASE_URL deve informar somente um nome de banco.")

    username = _decode_component(parsed.username, "usuário")
    password = _decode_component(parsed.password, "senha")
    database = _decode_component(raw_database, "banco")
    if not username or not database:
        raise ConfigurationError("DATABASE_URL contém componente obrigatório vazio.")

    libpq_environment = {
        "PGHOST": parsed.hostname,
        "PGUSER": username,
        "PGPASSWORD": password,
        "PGDATABASE": database,
    }
    if port is not None:
        libpq_environment["PGPORT"] = str(port)

    if parsed.query:
        if INVALID_PERCENT_ENCODING.search(parsed.query):
            raise ConfigurationError("Percent-encoding inválido na query da DATABASE_URL.")
        try:
            parameters = parse_qsl(
                parsed.query,
                keep_blank_values=True,
                strict_parsing=True,
                encoding="utf-8",
                errors="strict",
            )
        except (UnicodeDecodeError, ValueError) as exc:
            raise ConfigurationError("Query inválida na DATABASE_URL.") from exc

        seen_parameters: set[str] = set()
        for name, value in parameters:
            if name not in QUERY_PARAMETER_ENV:
                raise ConfigurationError(
                    "DATABASE_URL contém parâmetro de query não permitido."
                )
            if name in seen_parameters:
                raise ConfigurationError(
                    "DATABASE_URL contém parâmetro de query duplicado."
                )
            if "\x00" in value:
                raise ConfigurationError(
                    "DATABASE_URL contém valor de query inválido."
                )
            seen_parameters.add(name)
            libpq_environment[QUERY_PARAMETER_ENV[name]] = value

    return libpq_environment


def build_client_environment(
    environment: Mapping[str, str],
) -> dict[str, str]:
    """Crie ambiente controlado para o cliente sem propagar DATABASE_URL."""

    database_url = environment.get("DATABASE_URL")
    if not database_url:
        raise ConfigurationError("DATABASE_URL não está definida.")

    child_environment = {
        key: value
        for key, value in environment.items()
        if key != "DATABASE_URL" and not key.startswith("PG")
    }
    child_environment.update(parse_database_url(database_url))
    return child_environment


def main(arguments: Sequence[str] | None = None) -> int:
    client_arguments = list(arguments if arguments is not None else sys.argv[1:])
    if not client_arguments:
        print(
            "postgres_client: informe o executável PostgreSQL e seus argumentos.",
            file=sys.stderr,
        )
        return 2

    try:
        child_environment = build_client_environment(os.environ)
    except ConfigurationError as exc:
        print(f"postgres_client: erro: {exc}", file=sys.stderr)
        return 2

    executable = client_arguments[0]
    try:
        completed_process = subprocess.run(
            client_arguments,
            env=child_environment,
            check=False,
            shell=False,
        )
    except OSError:
        print(
            "postgres_client: não foi possível executar o cliente PostgreSQL.",
            file=sys.stderr,
        )
        return 127
    return completed_process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
