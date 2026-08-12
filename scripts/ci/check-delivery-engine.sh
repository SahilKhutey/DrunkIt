#!/bin/bash
set -e

echo "Checking Delivery System & Delivery Engine Architecture..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_delivery_engine.py

echo "✅ Delivery System & Delivery Engine Architecture verified cleanly."
