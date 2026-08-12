#!/bin/bash
set -e

echo "Checking API conventions and standard response envelope..."

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -c "
import sys
sys.path.insert(0, 'services/_common')
from faccp_common.dto.envelope import SuccessResponse, ErrorResponse, PaginatedResponse

res = SuccessResponse(data={'status': 'ok'})
assert res.success is True
print('✅ API envelope DTOs verified successfully.')
"
