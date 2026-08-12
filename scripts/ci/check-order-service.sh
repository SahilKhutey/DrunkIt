#!/bin/bash
set -e

echo "Checking Phase 6 Order Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_order_service.py

echo "✅ Phase 6 Order Service Microservice verified cleanly."
