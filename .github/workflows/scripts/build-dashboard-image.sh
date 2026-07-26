#!/bin/bash
# Script to build and push React dashboard Docker image
# Usage: ./build-dashboard-image.sh <image-tag>

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "❌ Usage: build-dashboard-image.sh <image-tag>"
    exit 1
fi

IMAGE_TAG=$1
REGISTRY_URL=${REGISTRY_URL:-"acrcountrystatsshow.azurecr.io"}
IMAGE_NAME="countrystats-dashboard"

echo "🐳 Building Docker image..."
docker build -f Dockerfile.dashboard -t ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG} .

if [ "${DOCKER_PUSH:-false}" = "true" ]; then
    echo "🚀 Pushing image to registry..."
    docker push ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}
    echo "✅ Image pushed successfully"
else
    echo "ℹ️ Docker push skipped (set DOCKER_PUSH=true to enable)"
fi
