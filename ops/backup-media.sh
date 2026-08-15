#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

PROGRAM_NAME="backup-media"
MEDIA_DIR="${MEDIA_BACKUP_SOURCE:-/srv/justica-climatica/media}"
BACKUP_DIR="${MEDIA_BACKUP_DIR:-/srv/justica-climatica/backups/media}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
TAR_BIN="${TAR_BIN:-tar}"
SHA256SUM_BIN="${SHA256SUM_BIN:-sha256sum}"
FLOCK_BIN="${FLOCK_BIN:-flock}"
DATE_BIN="${DATE_BIN:-date}"
MKTEMP_BIN="${MKTEMP_BIN:-mktemp}"
FIND_BIN="${FIND_BIN:-find}"
REALPATH_BIN="${REALPATH_BIN:-realpath}"

TEMP_ARCHIVE=""
TEMP_CHECKSUM=""
FINAL_ARCHIVE=""
FINAL_CHECKSUM=""
ARCHIVE_MOVED=0
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

    if [[ -n "$TEMP_ARCHIVE" && -e "$TEMP_ARCHIVE" ]]; then
        rm -f -- "$TEMP_ARCHIVE" || true
    fi
    if [[ -n "$TEMP_CHECKSUM" && -e "$TEMP_CHECKSUM" ]]; then
        rm -f -- "$TEMP_CHECKSUM" || true
    fi
    if (( COMPLETE == 0 )); then
        if (( CHECKSUM_MOVED == 1 )); then
            rm -f -- "$FINAL_CHECKSUM" || true
        fi
        if (( ARCHIVE_MOVED == 1 )); then
            rm -f -- "$FINAL_ARCHIVE" || true
        fi
    fi

    exit "$exit_code"
}

trap cleanup EXIT
trap 'exit 130' INT TERM HUP

[[ "$MEDIA_DIR" == /* ]] || fail "MEDIA_BACKUP_SOURCE deve ser um caminho absoluto."
[[ "$BACKUP_DIR" == /* ]] || fail "MEDIA_BACKUP_DIR deve ser um caminho absoluto."
[[ "$MEDIA_DIR" != "/" && "$BACKUP_DIR" != "/" ]] || fail "Diretórios não podem ser a raiz do sistema."
[[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || fail "BACKUP_RETENTION_DAYS deve ser inteiro não negativo."
[[ -d "$MEDIA_DIR" ]] || fail "Diretório de media não existe."
[[ ! -L "$MEDIA_DIR" ]] || fail "O diretório de media não pode ser link simbólico."
[[ ! -L "$BACKUP_DIR" ]] || fail "O diretório de backup não pode ser link simbólico."

if ! mkdir -p -- "$BACKUP_DIR"; then
    fail "Não foi possível preparar o diretório de backup."
fi
[[ -d "$BACKUP_DIR" && -w "$BACKUP_DIR" ]] || fail "Diretório de backup inválido ou sem escrita."
[[ ! -L "$BACKUP_DIR" ]] || fail "O diretório de backup não pode ser link simbólico."

for required_command in \
    "$TAR_BIN" "$SHA256SUM_BIN" "$FLOCK_BIN" "$DATE_BIN" \
    "$MKTEMP_BIN" "$FIND_BIN" "$REALPATH_BIN"; do
    require_command "$required_command"
done

media_real="$($REALPATH_BIN -e -- "$MEDIA_DIR")"
backup_real="$($REALPATH_BIN -e -- "$BACKUP_DIR")"
if [[ "$backup_real" == "$media_real" || "$backup_real" == "$media_real/"* ]]; then
    fail "O destino do backup não pode estar dentro do diretório de media."
fi

LOCK_FILE="${BACKUP_DIR}/.backup-media.lock"
[[ ! -L "$LOCK_FILE" ]] || fail "O arquivo de lock não pode ser link simbólico."
if ! { exec 9>"$LOCK_FILE"; }; then
    fail "Não foi possível abrir o lock do backup."
fi
if ! "$FLOCK_BIN" -n 9; then
    log "Outro backup de media já está em execução; encerrando sem alterações."
    exit 75
fi

timestamp="$($DATE_BIN -u +%Y%m%dT%H%M%SZ)"
[[ "$timestamp" =~ ^[0-9]{8}T[0-9]{6}Z$ ]] || fail "Não foi possível gerar timestamp UTC válido."

final_name="justica-climatica-media-${timestamp}.tar.gz"
FINAL_ARCHIVE="${BACKUP_DIR}/${final_name}"
FINAL_CHECKSUM="${FINAL_ARCHIVE}.sha256"
[[ ! -e "$FINAL_ARCHIVE" && ! -L "$FINAL_ARCHIVE" ]] || fail "Já existe backup com o timestamp atual."
[[ ! -e "$FINAL_CHECKSUM" && ! -L "$FINAL_CHECKSUM" ]] || fail "Já existe checksum com o timestamp atual."

TEMP_ARCHIVE="$($MKTEMP_BIN --tmpdir="$BACKUP_DIR" ".${final_name}.tmp.XXXXXX")"
TEMP_CHECKSUM="$($MKTEMP_BIN --tmpdir="$BACKUP_DIR" ".${final_name}.sha256.tmp.XXXXXX")"

log "Iniciando backup de media."
if ! "$TAR_BIN" \
    --create \
    --gzip \
    --file="$TEMP_ARCHIVE" \
    --directory="$MEDIA_DIR" \
    . \
    2>/dev/null; then
    fail "tar falhou; nenhum backup completo foi publicado."
fi
[[ -s "$TEMP_ARCHIVE" ]] || fail "tar não produziu arquivo válido."

if ! checksum_output="$($SHA256SUM_BIN "$TEMP_ARCHIVE" 2>/dev/null)"; then
    fail "Não foi possível calcular o checksum do backup."
fi
checksum="${checksum_output%%[[:space:]]*}"
[[ "$checksum" =~ ^[0-9a-fA-F]{64}$ ]] || fail "Checksum SHA-256 inválido."
printf '%s  %s\n' "$checksum" "$final_name" >"$TEMP_CHECKSUM"
[[ -s "$TEMP_CHECKSUM" ]] || fail "Não foi possível gerar o arquivo de checksum."

mv -- "$TEMP_ARCHIVE" "$FINAL_ARCHIVE"
TEMP_ARCHIVE=""
ARCHIVE_MOVED=1
mv -- "$TEMP_CHECKSUM" "$FINAL_CHECKSUM"
TEMP_CHECKSUM=""
CHECKSUM_MOVED=1
COMPLETE=1

log "Backup de media concluído: $FINAL_ARCHIVE"
log "Aplicando retenção de ${RETENTION_DAYS} dia(s)."
"$FIND_BIN" -P "$BACKUP_DIR" -xdev -maxdepth 1 -type f \
    \( -name 'justica-climatica-media-????????T??????Z.tar.gz' \
       -o -name 'justica-climatica-media-????????T??????Z.tar.gz.sha256' \) \
    -mtime "+${RETENTION_DAYS}" -print -delete
log "Retenção de media concluída."
