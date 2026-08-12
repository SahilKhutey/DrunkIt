#!/bin/bash
set -e

echo "Checking Phase 8 Risk Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_risk_service.py

echo "✅ Phase 8 Risk Service Microservice verified cleanly."
