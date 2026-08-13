#!/bin/bash
set -e

echo "Checking Phase 11 API Gateway Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_gateway_service.py

echo "✅ Phase 11 API Gateway Service Microservice verified cleanly."
