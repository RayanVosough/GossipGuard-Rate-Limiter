from __future__ import annotations

from app.models.enums import Permission, Role


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ANONYMOUS: {Permission.READ_PUBLIC},
    Role.VIEWER: {Permission.READ_PUBLIC, Permission.READ_PROFILE},
    Role.EDITOR: {Permission.READ_PUBLIC, Permission.READ_PROFILE, Permission.WRITE_CONTENT},
    Role.ADMIN: {
        Permission.READ_PUBLIC,
        Permission.READ_PROFILE,
        Permission.WRITE_CONTENT,
        Permission.MANAGE_USERS,
        Permission.VIEW_AUDIT_LOGS,
    },
}
