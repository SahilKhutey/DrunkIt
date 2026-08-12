#!/bin/bash
set -e

echo "Checking Product Catalog Admin System Architecture..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_product_catalog_admin.py

echo "✅ Product Catalog Admin System Architecture verified cleanly."
