from typing import Dict, Set
from .models import SystemRole, PermissionAction

# RBAC Resource Matrix Mapping [Role][ResourceType] -> Set of Allowed PermissionActions
RBAC_MATRIX: Dict[SystemRole, Dict[str, Set[PermissionAction]]] = {
    # System Root & Super Admin
    SystemRole.PLATFORM_ROOT: {
        "*": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.DELETE, PermissionAction.VERIFY, PermissionAction.APPROVE, PermissionAction.EXECUTE, PermissionAction.EXPORT}
    },
    SystemRole.SUPER_ADMIN: {
        "*": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.DELETE, PermissionAction.VERIFY, PermissionAction.APPROVE, PermissionAction.EXECUTE, PermissionAction.EXPORT}
    },

    # State & Regulatory Admins
    SystemRole.STATE_ADMIN: {
        "JURISDICTION": {PermissionAction.READ, PermissionAction.UPDATE},
        "POLICY_RULE": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE},
        "DRY_DAYS": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE},
        "RETAILER_APPLICATION": {PermissionAction.READ, PermissionAction.APPROVE},
        "EXCISE_LICENSE": {PermissionAction.READ, PermissionAction.VERIFY, PermissionAction.APPROVE, PermissionAction.EXECUTE},
        "AUDIT_EVENT": {PermissionAction.READ, PermissionAction.EXPORT}
    },

    # Compliance Officer
    SystemRole.COMPLIANCE_OFFICER: {
        "POLICY_RULE": {PermissionAction.CREATE, PermissionAction.READ},
        "DRY_DAYS": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE},
        "RETAILER_APPLICATION": {PermissionAction.READ, PermissionAction.VERIFY},
        "EXCISE_LICENSE": {PermissionAction.READ, PermissionAction.VERIFY},
        "RISK_ALERT": {PermissionAction.READ, PermissionAction.UPDATE},
        "AUDIT_EVENT": {PermissionAction.READ}
    },

    # Retailer Owner & Store Manager
    SystemRole.RETAILER_OWNER: {
        "ORGANIZATION": {PermissionAction.READ, PermissionAction.UPDATE},
        "STORE": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.DELETE},
        "EXCISE_LICENSE": {PermissionAction.CREATE, PermissionAction.READ},
        "STAFF": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.APPROVE},
        "PRICING": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.DELETE, PermissionAction.APPROVE},
        "INVENTORY": {PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.APPROVE},
        "ORDER": {PermissionAction.READ, PermissionAction.APPROVE, PermissionAction.EXECUTE}
    },
    SystemRole.STORE_MANAGER: {
        "STORE": {PermissionAction.READ, PermissionAction.UPDATE},
        "EXCISE_LICENSE": {PermissionAction.READ},
        "STAFF": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.APPROVE},
        "PRICING": {PermissionAction.READ, PermissionAction.UPDATE},
        "INVENTORY": {PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.APPROVE},
        "ORDER": {PermissionAction.READ, PermissionAction.APPROVE, PermissionAction.EXECUTE}
    },
    SystemRole.PACKER: {
        "INVENTORY": {PermissionAction.READ},
        "ORDER": {PermissionAction.READ, PermissionAction.EXECUTE}
    },

    # Delivery Agents
    SystemRole.DELIVERY_AGENT: {
        "ORDER": {PermissionAction.READ, PermissionAction.EXECUTE},
        "DELIVERY": {PermissionAction.READ, PermissionAction.VERIFY, PermissionAction.EXECUTE},
        "PROOF_OF_DELIVERY": {PermissionAction.CREATE, PermissionAction.UPDATE}
    },

    # Consumer Domain
    SystemRole.GUEST: {
        "PUBLIC_CATALOG": {PermissionAction.READ},
        "STORE_LISTING": {PermissionAction.READ}
    },
    SystemRole.REGISTERED: {
        "PUBLIC_CATALOG": {PermissionAction.READ},
        "STORE_LISTING": {PermissionAction.READ},
        "CART": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.DELETE},
        "IDENTITY_DOCUMENT": {PermissionAction.CREATE},
        "SUPPORT_TICKET": {PermissionAction.CREATE, PermissionAction.READ}
    },
    SystemRole.AGE_ELIGIBLE: {
        "PUBLIC_CATALOG": {PermissionAction.READ},
        "STORE_LISTING": {PermissionAction.READ},
        "CART": {PermissionAction.CREATE, PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.DELETE},
        "CHECKOUT": {PermissionAction.READ},
        "ORDER": {PermissionAction.CREATE, PermissionAction.READ},
        "AGE_VERIFICATION": {PermissionAction.VERIFY},
        "DELIVERY_TRACKING": {PermissionAction.READ}
    }
}

def check_rbac_permission(role: SystemRole, resource_type: str, action: PermissionAction) -> bool:
    role_perms = RBAC_MATRIX.get(role, {})
    
    # Platform Root & Super Admin wildcard check
    if "*" in role_perms and action in role_perms["*"]:
        return True

    # Resource type specific check
    resource_perms = role_perms.get(resource_type, set())
    return action in resource_perms
