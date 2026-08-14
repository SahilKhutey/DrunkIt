#!/usr/bin/env bash
set -Eeuo pipefail

NAMESPACE="drunkit"
RELEASE="drunkit"

echo "Rolling back DrunkIt release ${RELEASE}..."

helm rollback \
    "$RELEASE" \
    --namespace "$NAMESPACE" \
    --wait \
    --timeout 10m

echo "Rollback completed successfully."

kubectl get pods -n "$NAMESPACE"
