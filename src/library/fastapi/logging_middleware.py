"""FastAPI logging middleware for Agent Hub.

This middleware provides structured logging for HTTP requests, including
latency tracking and status code reporting.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from fastapi import Request, Response

logger = structlog.get_logger(__name__)


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    """FastAPI middleware to log HTTP request and response information.

    Args:
        request: The incoming FastAPI request.
        call_next: The next request handler in the chain.

    Returns:
        The FastAPI response.

    """
    logger.info(
        "HTTP request started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )
    start_time = time.perf_counter()

    # Process the request
    response = await call_next(request)

    # Calculate duration in milliseconds
    process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Log the result using structured logging
    logger.info(
        "HTTP request finished",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=process_time_ms,
        client_ip=request.client.host if request.client else None,
    )

    return response
