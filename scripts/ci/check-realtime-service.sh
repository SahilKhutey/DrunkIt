#!/bin/bash
set -e

echo "Checking Phase 8 Realtime Service Microservice..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_realtime_service.py

echo "✅ Phase 8 Realtime Service Microservice verified cleanly."
