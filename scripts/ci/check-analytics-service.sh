#!/bin/bash
set -e

echo "Checking Phase 9 Analytics Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_analytics_service.py

echo "✅ Phase 9 Analytics Service Microservice verified cleanly."
