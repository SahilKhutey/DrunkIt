#!/bin/bash
set -e

echo "Checking Product Platform Architecture..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_product_platform.py

echo "✅ Product Platform Architecture verified cleanly."
