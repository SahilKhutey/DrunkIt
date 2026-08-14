"""Consumer API security dependencies."""

from fastapi import Depends
from faccp_platform.security.dependencies import get_current_principal
from faccp_platform.security.principal import Principal


async def current_principal(
    principal: Principal = Depends(get_current_principal),
) -> Principal:
    """Extract authenticated Principal from HTTP Bearer credentials."""
    return principal
