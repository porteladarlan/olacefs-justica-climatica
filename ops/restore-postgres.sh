#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

PROGRAM_NAME="restore-postgres"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
POSTGRES_CLIENT_HELPER="${POSTGRES_CLIENT_HELPER:-${SCRIPT_DIR}/postgres_client.py}"
PG_RESTORE_BIN="${PG_RESTORE_BIN:-pg_restore}"
SHA256SUM_BIN="${SHA256SUM_BIN:-sha256sum}"
REALPATH_BIN="${REALPATH_BIN:-realpath}"

log() {
    printf '[%s] %s\n' "$PROGRAM_NAME" "$*"
}

fail() {
    log "ERRO: $*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Executável obrigatório indisponível."
}

[[ $# -eq 1 ]] || fail "Informe exatamente o caminho do arquivo .dump."
[[ "${ALLOW_DATABASE_RESTORE:-}" == "yes" ]] || fail "Defina ALLOW_DATABASE_RESTORE=yes para autorizar o restore."
[[ -n "${DATABASE_URL:-}" ]] || fail "DATABASE_URL não está definida."
[[ -f "$POSTGRES_CLIENT_HELPER" ]] || fail "Helper PostgreSQL obrigatório indisponível."

for required_command in "$PYTHON_BIN" "$PG_RESTORE_BIN" "$SHA256SUM_BIN" "$REALPATH_BIN"; do
    require_command "$required_command"
done

DUMP_ARGUMENT="$1"
[[ -f "$DUMP_ARGUMENT" ]] || fail "Arquivo de dump não existe ou não é regular."
[[ -s "$DUMP_ARGUMENT" ]] || fail "Arquivo de dump está vazio."
[[ ! -L "$DUMP_ARGUMENT" ]] || fail "Arquivo de dump não pode ser link simbólico."
DUMP_PATH="$($REALPATH_BIN -e -- "$DUMP_ARGUMENT")"

CHECKSUM_PATH="${DUMP_PATH}.sha256"
if [[ -e "$CHECKSUM_PATH" || -L "$CHECKSUM_PATH" ]]; then
    [[ -f "$CHECKSUM_PATH" ]] || fail "Checksum correspondente não é arquivo regular."
    [[ ! -L "$CHECKSUM_PATH" ]] || fail "Checksum não pode ser link simbólico."

    expected_checksum=""
    expected_filename=""
    extra_field=""
    IFS=' ' read -r expected_checksum expected_filename extra_field <"$CHECKSUM_PATH" || true
    [[ "$expected_checksum" =~ ^[0-9a-fA-F]{64}$ ]] || fail "Checksum esperado é inválido."
    [[ "$expected_filename" == "$(basename -- "$DUMP_PATH")" ]] || fail "Checksum não corresponde ao dump informado."
    [[ -z "$extra_field" ]] || fail "Arquivo de checksum contém campos inesperados."

    if ! checksum_output="$($SHA256SUM_BIN "$DUMP_PATH" 2>/dev/null)"; then
        fail "Não foi possível calcular o checksum do dump."
    fi
    actual_checksum="${checksum_output%%[[:space:]]*}"
    [[ "${actual_checksum,,}" == "${expected_checksum,,}" ]] || fail "Verificação SHA-256 falhou."
    log "Checksum SHA-256 verificado."
else
    if [[ "${ALLOW_RESTORE_WITHOUT_CHECKSUM:-}" != "yes" ]]; then
        fail "Checksum correspondente não encontrado; restore abortado."
    fi
    log "AVISO: restore sem checksum autorizado explicitamente."
fi

if ! "$PG_RESTORE_BIN" --list "$DUMP_PATH" >/dev/null 2>&1; then
    fail "O arquivo não é um dump PostgreSQL custom válido."
fi

log "Iniciando restore PostgreSQL autorizado em banco previamente preparado."
if ! "$PYTHON_BIN" "$POSTGRES_CLIENT_HELPER" \
    --database-argument \
    "$PG_RESTORE_BIN" \
    --exit-on-error \
    --single-transaction \
    --no-owner \
    --no-privileges \
    --no-password \
    "$DUMP_PATH" \
    >/dev/null 2>&1; then
    fail "pg_restore falhou por conexão, autenticação, permissão ou conflito de objetos; restore não foi concluído."
fi

log "Restore PostgreSQL concluído. Execute as validações funcionais antes de promover o banco."
