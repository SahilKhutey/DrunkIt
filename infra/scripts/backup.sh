#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DATABASE_URL="${DATABASE_URL:?DATABASE_URL required}"

pg_dump "$DATABASE_URL" --format=custom --file="/backup/drunkit_${TIMESTAMP}.dump"
