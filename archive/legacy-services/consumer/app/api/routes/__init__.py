"""Consumer API routes package."""

from .consumers import router as consumer_router
from .profiles import router as profile_router
from .verification import router as verification_router

__all__ = ["consumer_router", "profile_router", "verification_router"]
