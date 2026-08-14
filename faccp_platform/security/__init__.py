"""Platform Security Kernel package."""

from .authorization import (
    authorize_resource_access,
    can_access_resource,
    current_user,
    require_permission,
)
from .claims import TokenClaims
from .hashing import hash_password, verify_password
from .idempotency import IdempotencyRecord, calculate_payload_hash, validate_idempotency_key
from .jwt import JWTVerifier
from .middleware import request_size_limit_middleware, security_headers_middleware
from .permissions import Permission
from .secrets import SecretProvider
from .service_identity import (
    DELIVERY_SERVICE,
    INVENTORY_SERVICE,
    ORDER_SERVICE,
    PAYMENT_SERVICE,
    TRUSTED_SERVICES,
    SecurityContext,
    ServiceIdentity,
)

__all__ = [
    "DELIVERY_SERVICE",
    "INVENTORY_SERVICE",
    "ORDER_SERVICE",
    "PAYMENT_SERVICE",
    "TRUSTED_SERVICES",
    "IdempotencyRecord",
    "JWTVerifier",
    "Permission",
    "SecretProvider",
    "SecurityContext",
    "ServiceIdentity",
    "TokenClaims",
    "authorize_resource_access",
    "calculate_payload_hash",
    "can_access_resource",
    "current_user",
    "hash_password",
    "request_size_limit_middleware",
    "require_permission",
    "security_headers_middleware",
    "validate_idempotency_key",
    "verify_password",
]
