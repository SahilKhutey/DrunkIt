#!/bin/bash
set -e

echo "Checking Listing Engine Development Specification..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_listing_engine_spec.py

echo "✅ Listing Engine Development Specification verified cleanly."
