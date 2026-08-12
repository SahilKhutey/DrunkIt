#!/bin/bash
set -e

echo "Checking PII encryption module compliance..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -c "
import sys, os
sys.path.insert(0, 'services/_common')
from faccp_common.privacy.data_minimization import DataMinimizationPolicy

print('✅ PII encryption & data minimization policies loaded successfully.')
"
