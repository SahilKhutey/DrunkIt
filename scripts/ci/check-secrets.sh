#!/bin/bash
set -e

echo "Checking for hardcoded secrets in source files..."

# Scan for obvious hardcoded credentials
VIOLATIONS=$(grep -rE "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}['\"]" \
    --include="*.py" --include="*.ts" --include="*.tsx" \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv \
    services/ apps/ packages/ | grep -v "test" | grep -v "placeholder" | grep -v "example" || true)

if [ -n "$VIOLATIONS" ]; then
    echo "❌ HARDCODED SECRETS FOUND:"
    echo "$VIOLATIONS"
    exit 1
fi

echo "✅ Secret check passed cleanly."
