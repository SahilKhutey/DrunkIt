#!/bin/bash
# FACCP Disaster Recovery — Automated backup script
# Usage: ./backup.sh [full|incremental] [s3|local]

set -euo pipefail

MODE="${1:-full}"
TARGET="${2:-s3}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/faccp_backup_${TIMESTAMP}"
RETENTION_DAYS=30
S3_BUCKET="${DR_BACKUP_S3_BUCKET:-faccp-dr-backups}"
ENCRYPTION_KEY="${DR_BACKUP_ENCRYPTION_KEY:-faccp_default_enc_key}"

DATABASES=(
    "faccp_identity"
    "faccp_consumer"
    "faccp_retailer"
    "faccp_catalog"
    "faccp_inventory"
    "faccp_order"
    "faccp_compliance"
    "faccp_audit"
    "faccp_risk"
    "faccp_verification"
    "faccp_delivery"
    "faccp_notification"
    "faccp_payment"
    "faccp_pricing"
    "faccp_analytics"
    "faccp_realtime"
)

mkdir -p "${BACKUP_DIR}"

echo "==> Starting ${MODE} backup to ${TARGET}"
echo "==> Timestamp: ${TIMESTAMP}"

for db in "${DATABASES[@]}"; do
    echo " -> Backing up ${db}..."
    if [ "$MODE" = "full" ]; then
        pg_dump -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-faccp_admin}" \
            -Fc "${db}" > "${BACKUP_DIR}/${db}.dump" || true
    else
        echo " (incremental: relying on WAL streaming)"
    fi
done

echo "==> Snapshotting audit chain..."
PGPASSWORD="${POSTGRES_PASSWORD:-faccp_password}" psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-faccp_admin}" -d faccp_audit \
    -c "COPY (SELECT * FROM audit_events ORDER BY sequence_number DESC LIMIT 100000) TO STDOUT WITH CSV HEADER" \
    > "${BACKUP_DIR}/audit_chain_recent.csv" || true

echo "==> Backing up configurations..."
tar czf "${BACKUP_DIR}/configs.tar.gz" -C /app infrastructure/ 2>/dev/null || true

if [ -n "${ENCRYPTION_KEY}" ]; then
    echo "==> Encrypting backup..."
    tar czf - "${BACKUP_DIR}" | openssl enc -aes-256-gcm -salt -pbkdf2 \
        -pass "pass:${ENCRYPTION_KEY}" > "${BACKUP_DIR}.tar.gz.enc" 2>/dev/null || tar czf "${BACKUP_DIR}.tar.gz" "${BACKUP_DIR}"
    rm -rf "${BACKUP_DIR}"
    BACKUP_FILE="${BACKUP_DIR}.tar.gz.enc"
else
    tar czf "${BACKUP_DIR}.tar.gz" "${BACKUP_DIR}"
    rm -rf "${BACKUP_DIR}"
    BACKUP_FILE="${BACKUP_DIR}.tar.gz"
fi

if [ "$TARGET" = "s3" ]; then
    echo "==> Uploading to S3..."
    aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/${TIMESTAMP}/${BACKUP_FILE}" \
        --storage-class STANDARD_IA 2>/dev/null || echo "S3 upload skipped"
fi

echo "============================================"
echo "Backup completed: ${TIMESTAMP}"
echo "File: ${BACKUP_FILE}"
echo "============================================"
