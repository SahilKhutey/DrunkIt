class ProductStatus:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEW = "REVIEW"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class ListingStatus:
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BLOCKED = "BLOCKED"


ALLOWED_PRODUCT_TRANSITIONS = {
    "DRAFT": {"SUBMITTED"},
    "SUBMITTED": {"REVIEW"},
    "REVIEW": {"APPROVED", "REJECTED"},
    "APPROVED": {"ACTIVE"},
    "ACTIVE": {"SUSPENDED", "RETIRED"},
    "SUSPENDED": {"ACTIVE", "RETIRED"},
}


def validate_transition(current: str, target: str) -> bool:
    allowed = ALLOWED_PRODUCT_TRANSITIONS.get(current, set())

    if target not in allowed:
        raise ValueError(f"Invalid transition: {current} -> {target}")

    return True
