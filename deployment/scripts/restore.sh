#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_FILE="${1:?Backup file required}"
DATABASE_URL="${DATABASE_URL:?DATABASE_URL required}"

pg_restore --clean --if-exists --dbname="$DATABASE_URL" "$BACKUP_FILE"

echo "Database restoration completed successfully."
