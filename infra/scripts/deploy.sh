#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="drunkit"

kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/config/
kubectl apply -f infra/kubernetes/order/
kubectl rollout status deployment/order-service -n "$NAMESPACE"
