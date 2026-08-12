#!/bin/bash
set -e

echo "Checking Domain Isolation & Bounded Contexts..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_domain_isolation.py

echo "✅ Domain Isolation Protocol verified cleanly."
