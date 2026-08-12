#!/bin/bash
set -e

echo "Checking Phase 3 Consumer Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_consumer_service.py

echo "✅ Phase 3 Consumer Service Microservice verified cleanly."
