#!/usr/bin/env bash
set -Eeuo pipefail

echo "======================================"
echo " DrunkIt Production Preflight Check"
echo "======================================"

fail() {
    echo "[FAIL] $1"
    exit 1
}

pass() {
    echo "[PASS] $1"
}

command -v docker >/dev/null || fail "Docker missing"
command -v kubectl >/dev/null || fail "kubectl missing"
command -v helm >/dev/null || fail "Helm missing"
command -v git >/dev/null || fail "Git missing"

pass "Required CLI tools verified"

git diff --quiet || echo "[WARN] Git working tree contains uncommitted changes"

echo "Preflight check completed successfully."
