#!/usr/bin/env bash
set -Eeuo pipefail

echo "Running database migrations..."

alembic upgrade head

CURRENT=$(alembic current)
HEAD=$(alembic heads)

echo "Current revision: ${CURRENT}"
echo "Head revision:    ${HEAD}"

echo "Database migration completed successfully."
