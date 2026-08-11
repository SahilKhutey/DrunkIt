#!/bin/bash
# FACCP Disaster Recovery — Restore from backup
# Usage: ./restore.sh <backup_file> [target_db_prefix]

set -euo pipefail

BACKUP_FILE="${1:-}"
TARGET_PREFIX="${2:-faccp}"

if [ -z "${BACKUP_FILE}" ] || [ ! -f "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file> [target_db_prefix]"
    echo "Example: $0 /backups/faccp_backup_20250115.tar.gz.enc"
    exit 1
fi

echo "==> WARNING: This will overwrite existing databases"
echo "==> Backup file: ${BACKUP_FILE}"
echo "==> Target prefix: ${TARGET_PREFIX}"

WORK_DIR=$(mktemp -d)
trap "rm -rf ${WORK_DIR}" EXIT

if [[ "${BACKUP_FILE}" == *.enc ]]; then
    echo "==> Decrypting..."
    openssl enc -aes-256-gcm -d -pbkdf2 -pass "pass:${DR_BACKUP_ENCRYPTION_KEY:-faccp_default_enc_key}" \
        -in "${BACKUP_FILE}" -out "${WORK_DIR}/backup.tar.gz" 2>/dev/null || cp "${BACKUP_FILE}" "${WORK_DIR}/backup.tar.gz"
else
    cp "${BACKUP_FILE}" "${WORK_DIR}/backup.tar.gz"
fi

echo "==> Extracting..."
tar xzf "${WORK_DIR}/backup.tar.gz" -C "${WORK_DIR}/"
EXTRACTED_DIR=$(find "${WORK_DIR}" -mindepth 1 -maxdepth 1 -type d | head -1)

echo "==> Restoring databases..."
for dump in "${EXTRACTED_DIR}"/*.dump; do
    if [ -f "$dump" ]; then
        db_name=$(basename "$dump" .dump)
        echo " -> Restoring ${db_name}..."
        PGPASSWORD="${POSTGRES_PASSWORD:-faccp_password}" pg_restore -h "${POSTGRES_HOST:-localhost}" \
            -U "${POSTGRES_USER:-faccp_admin}" -d "${db_name}" --clean --if-exists --no-owner "$dump" || true
    fi
done

echo "============================================"
echo "Restore process finished."
echo "============================================"
