#!/bin/bash
set -e

echo "Checking Phase 4 Retailer Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_retailer_service.py

echo "✅ Phase 4 Retailer Service Microservice verified cleanly."
