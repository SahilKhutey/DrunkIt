#!/bin/bash
set -e

echo "Checking Source-of-Truth Protocol & Data Ownership Boundaries..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_source_of_truth.py

echo "✅ Source-of-Truth Protocol verified cleanly."
