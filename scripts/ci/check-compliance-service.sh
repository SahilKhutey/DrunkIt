#!/bin/bash
set -e

echo "Checking Phase 2 Compliance Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_compliance_service.py

echo "✅ Phase 2 Compliance Service Microservice verified cleanly."
