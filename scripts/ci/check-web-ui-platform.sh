#!/bin/bash
set -e

echo "Checking Web UI Platform Architecture..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_web_ui_platform.py

echo "✅ Web UI Platform Architecture verified cleanly."
