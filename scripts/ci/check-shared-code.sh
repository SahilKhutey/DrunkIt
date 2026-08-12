#!/bin/bash
set -e

echo "Checking Shared Code Purity in services/_common..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_shared_code.py

echo "✅ Shared Code Purity verified cleanly."
