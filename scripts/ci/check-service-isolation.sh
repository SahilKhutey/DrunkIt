#!/bin/bash
set -e

echo "Checking Database & Service Boundaries Isolation..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -c "
import sys, os
sys.path.insert(0, 'scripts/constitution')
from check_compliance import ConstitutionChecker

checker = ConstitutionChecker()
violations = checker.check_data()

if violations:
    print('❌ SERVICE ISOLATION VIOLATIONS DETECTED:')
    for v in violations:
        print(f'  - {v}')
    sys.exit(1)

print('✅ Service isolation verification passed.')
"
