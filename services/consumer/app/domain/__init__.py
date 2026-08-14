"""Consumer domain package."""

from .enums import ConsumerStatus, ProfileVisibility, VerificationMethod, VerificationStatus
from .errors import (
    ConsumerAlreadyExistsError,
    ConsumerDomainError,
    ConsumerNotFoundError,
    InvalidStateTransitionError,
)
from .events import (
    ConsumerActivatedEvent,
    ConsumerCreatedEvent,
    ConsumerVerificationCompletedEvent,
)

__all__ = [
    "ConsumerActivatedEvent",
    "ConsumerAlreadyExistsError",
    "ConsumerCreatedEvent",
    "ConsumerDomainError",
    "ConsumerNotFoundError",
    "ConsumerStatus",
    "ConsumerVerificationCompletedEvent",
    "InvalidStateTransitionError",
    "ProfileVisibility",
    "VerificationMethod",
    "VerificationStatus",
]
