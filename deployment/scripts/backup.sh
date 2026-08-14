#!/usr/bin/env bash
set -Eeuo pipefail

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
DATABASE_URL="${DATABASE_URL:?DATABASE_URL required}"
FILE="/backup/drunkit_${TIMESTAMP}.dump"

pg_dump "$DATABASE_URL" --format=custom --file="$FILE"
test -s "$FILE"

echo "Backup created successfully: ${FILE}"
