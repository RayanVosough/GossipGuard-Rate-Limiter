from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    ANONYMOUS = "anonymous"
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"


class Permission(str, Enum):
    READ_PUBLIC = "read_public"
    READ_PROFILE = "read_profile"
    WRITE_CONTENT = "write_content"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
