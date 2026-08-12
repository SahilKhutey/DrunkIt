#!/bin/bash
set -e

echo "Verifying test suite presence and structure..."

if [ ! -d "tests" ]; then
    echo "❌ Tests directory missing!"
    exit 1
fi

echo "✅ Test directory verified."
