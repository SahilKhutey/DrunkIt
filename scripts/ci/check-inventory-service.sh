#!/bin/bash
set -e

echo "Checking Phase 5 Inventory Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_inventory_service.py

echo "✅ Phase 5 Inventory Service Microservice verified cleanly."
