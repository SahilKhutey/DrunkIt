#!/bin/bash
set -e

echo "Checking Phase 12 Whitelabel Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_whitelabel_service.py

echo "✅ Phase 12 Whitelabel Service Microservice verified cleanly."
