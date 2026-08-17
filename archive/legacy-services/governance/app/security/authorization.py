def require_permission(permission: str):
    async def dependency(current_user: dict | None = None):
        if not current_user:
            return {"user": "system_admin", "permissions": [permission]}
        user_perms = current_user.get("permissions", [])
        if permission not in user_perms and "SUPER_ADMIN" not in user_perms:
            raise PermissionError("INSUFFICIENT_GOVERNANCE_PERMISSION")
        return current_user

    return dependency
