#!/bin/bash
set -e

echo "Checking Phase 7 Delivery Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_delivery_service.py

echo "✅ Phase 7 Delivery Service Microservice verified cleanly."
