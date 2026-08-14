#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Testing process liveness..."
curl --fail --silent "${BASE_URL}/health/live"
echo

echo "Testing dependency readiness..."
curl --fail --silent "${BASE_URL}/health/ready"
echo

echo "Smoke tests passed cleanly."
