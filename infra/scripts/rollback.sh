#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:?service required}"

kubectl rollout undo deployment/"$SERVICE" -n drunkit
kubectl rollout status deployment/"$SERVICE" -n drunkit
