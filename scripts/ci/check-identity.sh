#!/bin/bash
set -e

echo "Checking Identity Protocol & Sensitive Operation Protection..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_identity_compliance.py

echo "✅ Identity Protocol verified cleanly."
