#!/bin/bash
set -e

echo "Checking Single Responsibility Protocol & God Service Limits..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_single_responsibility.py

echo "✅ Single Responsibility Protocol verified cleanly."
