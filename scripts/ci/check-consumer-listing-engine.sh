#!/bin/bash
set -e

echo "Checking Consumer Listing Engine Architecture..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_consumer_listing_engine.py

echo "✅ Consumer Listing Engine Architecture verified cleanly."
