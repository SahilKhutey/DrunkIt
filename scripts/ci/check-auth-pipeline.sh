#!/bin/bash
set -e

echo "Checking Authentication, Authorization, & Trust Pipeline (Protocols 15, 16, 17)..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_auth_pipeline.py

echo "✅ Protocols 15, 16, & 17 verified cleanly."
