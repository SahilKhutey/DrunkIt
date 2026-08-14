#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-http://localhost:8000}"

echo "Checking process liveness..."
curl --fail "${HOST}/health/live"

echo "Checking dependency readiness..."
curl --fail "${HOST}/health/ready"
