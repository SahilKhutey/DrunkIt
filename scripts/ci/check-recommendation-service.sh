#!/bin/bash
set -e

echo "Checking Phase 10 Recommendation Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_recommendation_service.py

echo "✅ Phase 10 Recommendation Service Microservice verified cleanly."
