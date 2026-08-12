#!/bin/bash
set -e

echo "Checking Phase 1 Identity Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_identity_service.py

echo "✅ Phase 1 Identity Service Microservice verified cleanly."
