#!/bin/bash
set -e

echo "Checking Communication System Architecture (5 Layers & Envelopes)..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_communication_system.py

echo "✅ Communication System verified cleanly."
