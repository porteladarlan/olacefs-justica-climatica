#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

PROGRAM_NAME="healthcheck"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-https://olacefs-justiciaclimatica.gizapps.org.br/health/}"
CONNECT_TIMEOUT="${HEALTHCHECK_CONNECT_TIMEOUT:-5}"
MAX_TIME="${HEALTHCHECK_MAX_TIME:-15}"
CURL_BIN="${CURL_BIN:-curl}"
GREP_BIN="${GREP_BIN:-grep}"
MKTEMP_BIN="${MKTEMP_BIN:-mktemp}"
TEMP_DIR="${HEALTHCHECK_TMP_DIR:-${TMPDIR:-/tmp}}"
TEMP_RESPONSE=""

log() {
    printf '[%s] %s\n' "$PROGRAM_NAME" "$*"
}

fail() {
    log "ERRO: $*" >&2
    exit 1
}

cleanup() {
    local exit_code=$?
    trap - EXIT
    if [[ -n "$TEMP_RESPONSE" && -e "$TEMP_RESPONSE" ]]; then
        rm -f -- "$TEMP_RESPONSE" || true
    fi
    exit "$exit_code"
}

trap cleanup EXIT
trap 'exit 130' INT TERM HUP

command -v "$CURL_BIN" >/dev/null 2>&1 || fail "curl não está disponível."
command -v "$GREP_BIN" >/dev/null 2>&1 || fail "grep não está disponível."
command -v "$MKTEMP_BIN" >/dev/null 2>&1 || fail "mktemp não está disponível."

[[ "$HEALTHCHECK_URL" =~ ^https?:// ]] || fail "HEALTHCHECK_URL deve usar HTTP ou HTTPS."
url_authority="${HEALTHCHECK_URL#*://}"
url_authority="${url_authority%%/*}"
[[ "$url_authority" != *"@"* ]] || fail "HEALTHCHECK_URL não pode conter credenciais."
[[ "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]*$ ]] || fail "HEALTHCHECK_CONNECT_TIMEOUT deve ser inteiro positivo."
[[ "$MAX_TIME" =~ ^[1-9][0-9]*$ ]] || fail "HEALTHCHECK_MAX_TIME deve ser inteiro positivo."
[[ -d "$TEMP_DIR" && -w "$TEMP_DIR" ]] || fail "Diretório temporário inválido ou sem escrita."
[[ ! -L "$TEMP_DIR" ]] || fail "Diretório temporário não pode ser link simbólico."

TEMP_RESPONSE="$($MKTEMP_BIN --tmpdir="$TEMP_DIR" 'justica-health.XXXXXX')"

if ! http_status="$($CURL_BIN \
    --silent \
    --connect-timeout "$CONNECT_TIMEOUT" \
    --max-time "$MAX_TIME" \
    --max-filesize 1048576 \
    --output "$TEMP_RESPONSE" \
    --write-out '%{http_code}' \
    "$HEALTHCHECK_URL" \
    2>/dev/null)"; then
    fail "Falha ao consultar o health check."
fi

[[ "$http_status" == "200" ]] || fail "Health check retornou HTTP diferente de 200."
if ! LC_ALL=C "$GREP_BIN" -Eq '"status"[[:space:]]*:[[:space:]]*"ok"' "$TEMP_RESPONSE"; then
    fail "Health check não confirmou status ok."
fi
if ! LC_ALL=C "$GREP_BIN" -Eq '"database"[[:space:]]*:[[:space:]]*"ok"' "$TEMP_RESPONSE"; then
    fail "Health check não confirmou database ok."
fi

log "Health check concluído com sucesso."
