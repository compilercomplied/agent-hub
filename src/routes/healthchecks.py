from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health check endpoint")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Status information.

    """
    return {"status": "healthy"}
