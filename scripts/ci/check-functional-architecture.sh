#!/bin/bash
set -e

echo "Checking Functional Architecture (13 Domains & 71 Modules)..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_functional_architecture.py

echo "✅ Functional Architecture verified cleanly."
