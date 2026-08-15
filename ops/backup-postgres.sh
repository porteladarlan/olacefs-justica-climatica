#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

PROGRAM_NAME="backup-postgres"
BACKUP_DIR="${POSTGRES_BACKUP_DIR:-/srv/justica-climatica/backups/postgres}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
PG_DUMP_BIN="${PG_DUMP_BIN:-pg_dump}"
SHA256SUM_BIN="${SHA256SUM_BIN:-sha256sum}"
FLOCK_BIN="${FLOCK_BIN:-flock}"
DATE_BIN="${DATE_BIN:-date}"
MKTEMP_BIN="${MKTEMP_BIN:-mktemp}"
FIND_BIN="${FIND_BIN:-find}"

TEMP_DUMP=""
TEMP_CHECKSUM=""
FINAL_DUMP=""
FINAL_CHECKSUM=""
DUMP_MOVED=0
CHECKSUM_MOVED=0
COMPLETE=0

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

cleanup() {
    local exit_code=$?
    trap - EXIT

    if [[ -n "$TEMP_DUMP" && -e "$TEMP_DUMP" ]]; then
        rm -f -- "$TEMP_DUMP" || true
    fi
    if [[ -n "$TEMP_CHECKSUM" && -e "$TEMP_CHECKSUM" ]]; then
        rm -f -- "$TEMP_CHECKSUM" || true
    fi
    if (( COMPLETE == 0 )); then
        if (( CHECKSUM_MOVED == 1 )); then
            rm -f -- "$FINAL_CHECKSUM" || true
        fi
        if (( DUMP_MOVED == 1 )); then
            rm -f -- "$FINAL_DUMP" || true
        fi
    fi

    exit "$exit_code"
}

trap cleanup EXIT
trap 'exit 130' INT TERM HUP

[[ -n "${DATABASE_URL:-}" ]] || fail "DATABASE_URL não está definida."
database_connection="$DATABASE_URL"
unset DATABASE_URL
[[ "$BACKUP_DIR" == /* ]] || fail "POSTGRES_BACKUP_DIR deve ser um caminho absoluto."
[[ "$BACKUP_DIR" != "/" ]] || fail "POSTGRES_BACKUP_DIR não pode ser a raiz do sistema."
[[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || fail "BACKUP_RETENTION_DAYS deve ser inteiro não negativo."
[[ ! -L "$BACKUP_DIR" ]] || fail "O diretório de backup não pode ser link simbólico."

if ! mkdir -p -- "$BACKUP_DIR"; then
    fail "Não foi possível preparar o diretório de backup."
fi
[[ -d "$BACKUP_DIR" && -w "$BACKUP_DIR" ]] || fail "Diretório de backup inválido ou sem escrita."
[[ ! -L "$BACKUP_DIR" ]] || fail "O diretório de backup não pode ser link simbólico."

for required_command in \
    "$PG_DUMP_BIN" "$SHA256SUM_BIN" "$FLOCK_BIN" \
    "$DATE_BIN" "$MKTEMP_BIN" "$FIND_BIN"; do
    require_command "$required_command"
done

LOCK_FILE="${BACKUP_DIR}/.backup-postgres.lock"
[[ ! -L "$LOCK_FILE" ]] || fail "O arquivo de lock não pode ser link simbólico."
if ! { exec 9>"$LOCK_FILE"; }; then
    fail "Não foi possível abrir o lock do backup."
fi
if ! "$FLOCK_BIN" -n 9; then
    log "Outro backup PostgreSQL já está em execução; encerrando sem alterações."
    exit 75
fi

timestamp="$($DATE_BIN -u +%Y%m%dT%H%M%SZ)"
[[ "$timestamp" =~ ^[0-9]{8}T[0-9]{6}Z$ ]] || fail "Não foi possível gerar timestamp UTC válido."

final_name="justica-climatica-${timestamp}.dump"
FINAL_DUMP="${BACKUP_DIR}/${final_name}"
FINAL_CHECKSUM="${FINAL_DUMP}.sha256"
[[ ! -e "$FINAL_DUMP" && ! -L "$FINAL_DUMP" ]] || fail "Já existe backup com o timestamp atual."
[[ ! -e "$FINAL_CHECKSUM" && ! -L "$FINAL_CHECKSUM" ]] || fail "Já existe checksum com o timestamp atual."

TEMP_DUMP="$($MKTEMP_BIN --tmpdir="$BACKUP_DIR" ".${final_name}.tmp.XXXXXX")"
TEMP_CHECKSUM="$($MKTEMP_BIN --tmpdir="$BACKUP_DIR" ".${final_name}.sha256.tmp.XXXXXX")"

log "Iniciando backup PostgreSQL."
if ! PGDATABASE="$database_connection" "$PG_DUMP_BIN" \
    --format=custom \
    --file="$TEMP_DUMP" \
    --no-password \
    2>/dev/null; then
    fail "pg_dump falhou por conexão, autenticação, permissão ou gravação; nenhum backup completo foi publicado."
fi
database_connection=""
[[ -s "$TEMP_DUMP" ]] || fail "pg_dump não produziu arquivo válido."

if ! checksum_output="$($SHA256SUM_BIN "$TEMP_DUMP" 2>/dev/null)"; then
    fail "Não foi possível calcular o checksum do backup."
fi
checksum="${checksum_output%%[[:space:]]*}"
[[ "$checksum" =~ ^[0-9a-fA-F]{64}$ ]] || fail "Checksum SHA-256 inválido."
printf '%s  %s\n' "$checksum" "$final_name" >"$TEMP_CHECKSUM"
[[ -s "$TEMP_CHECKSUM" ]] || fail "Não foi possível gerar o arquivo de checksum."

mv -- "$TEMP_DUMP" "$FINAL_DUMP"
TEMP_DUMP=""
DUMP_MOVED=1
mv -- "$TEMP_CHECKSUM" "$FINAL_CHECKSUM"
TEMP_CHECKSUM=""
CHECKSUM_MOVED=1
COMPLETE=1

log "Backup PostgreSQL concluído: $FINAL_DUMP"
log "Aplicando retenção de ${RETENTION_DAYS} dia(s)."
"$FIND_BIN" -P "$BACKUP_DIR" -xdev -maxdepth 1 -type f \
    \( -name 'justica-climatica-????????T??????Z.dump' \
       -o -name 'justica-climatica-????????T??????Z.dump.sha256' \) \
    -mtime "+${RETENTION_DAYS}" -print -delete
log "Retenção PostgreSQL concluída."
