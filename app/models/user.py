from __future__ import annotations

from dataclasses import dataclass

from app.models.enums import Role


@dataclass(slots=True, frozen=True)
class User:
    username: str
    user_id: str
    email: str
    role: Role
