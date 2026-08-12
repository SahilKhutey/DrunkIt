#!/bin/bash
set -e

echo "Checking Phase 0 Foundation Execution..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_phase0_foundation.py

echo "✅ Phase 0 Foundation Execution verified cleanly."
