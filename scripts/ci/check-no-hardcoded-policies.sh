#!/bin/bash
set -e

echo "Checking for hardcoded compliance rules in service logic..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -c "
import sys, os
sys.path.insert(0, 'services/_common')
from faccp_common.compliance.policy_access import PolicyAccessGuard

violations = []
for root, _, files in os.walk('services/'):
    if '_common' in root: continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                v = PolicyAccessGuard.audit(path, fh.read())
                violations.extend(v)

if violations:
    print('❌ COMPLIANCE RULE HARDCODING VIOLATIONS DETECTED:')
    for v in violations:
        print(f'  - {v}')
    sys.exit(1)

print('✅ No hardcoded compliance rules found across services.')
"
