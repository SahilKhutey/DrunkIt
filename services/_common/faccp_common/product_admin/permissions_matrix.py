"""
Admin vs Retailer Product Permission Matrix.
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar


class PermissionAction(str, Enum):
    CREATE_PRODUCT_MASTER = "create_product_master"
    EDIT_PRODUCT_MASTER = "edit_product_master"
    CREATE_CATEGORY = "create_category"
    CREATE_SKU = "create_sku"
    CREATE_STORE_LISTING = "create_store_listing"
    SET_STORE_PRICE = "set_store_price"
    MANAGE_STORE_INVENTORY = "manage_store_inventory"
    SUSPEND_PRODUCT_GLOBALLY = "suspend_product_globally"
    REMOVE_FROM_OWN_STORE = "remove_from_own_store"


class AdminRetailerPermissionsMatrix:
    ADMIN_PERMISSIONS: ClassVar[set[PermissionAction]] = {
        PermissionAction.CREATE_PRODUCT_MASTER,
        PermissionAction.EDIT_PRODUCT_MASTER,
        PermissionAction.CREATE_CATEGORY,
        PermissionAction.CREATE_SKU,
        PermissionAction.CREATE_STORE_LISTING,
        PermissionAction.SUSPEND_PRODUCT_GLOBALLY,
        PermissionAction.REMOVE_FROM_OWN_STORE,
    }

    RETAILER_PERMISSIONS: ClassVar[set[PermissionAction]] = {
        PermissionAction.CREATE_STORE_LISTING,
        PermissionAction.SET_STORE_PRICE,
        PermissionAction.MANAGE_STORE_INVENTORY,
        PermissionAction.REMOVE_FROM_OWN_STORE,
    }

    @classmethod
    def can_admin(cls, action: PermissionAction) -> bool:
        return action in cls.ADMIN_PERMISSIONS

    @classmethod
    def can_retailer(cls, action: PermissionAction) -> bool:
        return action in cls.RETAILER_PERMISSIONS
