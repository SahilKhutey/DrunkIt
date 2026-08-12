#!/bin/bash
set -e

echo "Checking Development Gate System (Protocol 60 & 8 Gates)..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_development_gates.py

echo "✅ Protocol 60 & 8 Development Gates verified cleanly."
