#!/usr/bin/env bash
set -Eeuo pipefail

NAMESPACE="drunkit"
RELEASE="drunkit"
IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG required}"

echo "Deploying DrunkIt release ${RELEASE} with image tag ${IMAGE_TAG}..."

helm upgrade \
    --install \
    "$RELEASE" \
    infra/helm/drunkit \
    --namespace "$NAMESPACE" \
    --create-namespace \
    --set global.imageTag="$IMAGE_TAG" \
    --atomic \
    --timeout 10m

echo "Deployment completed successfully."
