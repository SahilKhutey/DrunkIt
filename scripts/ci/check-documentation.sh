#!/bin/bash
set -e

echo "Checking required architecture and protocol documentation..."

if [ ! -f "docs/protocols/FUNDAMENTAL_DEVELOPMENT_PROTOCOLS.md" ]; then
    echo "❌ Fundamental Development Protocols documentation missing!"
    exit 1
fi

echo "✅ Fundamental Development Protocols documentation verified."
