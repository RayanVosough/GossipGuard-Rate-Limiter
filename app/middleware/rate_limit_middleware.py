from __future__ import annotations

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.security import get_current_user_from_request
from app.services.rate_limit_service import RateLimitService


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service: RateLimitService) -> None:
        super().__init__(app)
        self.service = service

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.startswith("/internal/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        user = get_current_user_from_request(request)

        user_key = client_ip if user is None else f"{client_ip}:{user.user_id}"
        allowed, current_total, limit = await self.service.allow_request(user_key=user_key, user=user)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": limit,
                    "current_total": current_total,
                    "user_key": user_key,
                },
            )

        if user is not None:
            request.state.principal = user

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Current"] = str(current_total)
        return response
