#!/bin/bash
set -e

echo "Checking Catalog & Template Platform Architecture..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_catalog_and_templates.py

echo "✅ Catalog & Template Platform verified cleanly."
