#!/bin/bash
set -e

echo "Checking Event standards and event envelope implementation..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -c "
import sys
sys.path.insert(0, 'services/_common')
from faccp_common.events import make_event

evt = make_event('order.created', {'order_id': '123'}, producer='order-service')
assert evt['event_type'] == 'order.created'
print('✅ Event envelope standard verified successfully.')
"
