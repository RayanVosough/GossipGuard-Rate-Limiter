from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import require_permissions
from app.models.enums import Permission
from app.models.user import User

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/public")
async def public_scope() -> dict[str, str]:
    return {"message": "public content"}


@router.get("/profile")
async def profile(current_user: User = Depends(require_permissions(Permission.READ_PROFILE))) -> dict[str, str]:
    return {"message": f"Hello {current_user.email}", "role": current_user.role.value}


@router.get("/admin")
async def admin_area(current_user: User = Depends(require_permissions(Permission.MANAGE_USERS))) -> dict[str, str]:
    return {"message": f"Admin access granted to {current_user.user_id}"}
