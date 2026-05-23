"""Optional bearer-token auth. Off by default; enable by setting
``CHEMCLAW_RETRO_AUTH_TOKEN``."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from ..config import get_settings


async def require_token(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if settings.auth_token is None:
        return
    expected = f"Bearer {settings.auth_token}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing bearer token",
        )
