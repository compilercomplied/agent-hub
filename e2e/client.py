"""HTTP client configuration for e2e tests.

This module provides the HTTP client setup for black-box testing
of the API without importing the application code.
"""

from __future__ import annotations

import os
import time
from collections.abc import Generator
from functools import wraps
from typing import Any, Callable

import httpx


def with_retries(max_retries: int = 3, base_delay: float = 1.0) -> Callable:
    """Decorator to add retries with exponential backoff to client methods.

    Retries on connection errors and 5xx status codes.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            response = None
            for attempt in range(max_retries + 1):
                try:
                    response = func(*args, **kwargs)
                    # Retry on 5xx errors (transient K8s issues like port binding)
                    if 500 <= response.status_code < 600 and attempt < max_retries:
                        delay = base_delay * (2**attempt)
                        time.sleep(delay)
                        continue
                    return response
                except (httpx.RequestError, httpx.TimeoutException) as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2**attempt)
                        time.sleep(delay)
                        continue
            if last_exception:
                raise last_exception
            return response

        return wrapper

    return decorator


class CustomClient(httpx.Client):
    """An httpx Client with built-in retries and exponential backoff."""

    @with_retries()
    def get(self, *args: Any, **kwargs: Any) -> httpx.Response:
        return super().get(*args, **kwargs)

    @with_retries()
    def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
        return super().post(*args, **kwargs)


def get_base_url() -> str:
    """Get the base URL for the API.

    Returns:
        str: The base URL from environment variable or default.

    """
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


def get_client() -> Generator[CustomClient, None, None]:
    """Get an HTTP client configured for the API.

    Yields:
        CustomClient: A configured HTTP client instance.

    """
    base_url = get_base_url()
    with CustomClient(base_url=base_url, timeout=120.0) as client:
        yield client


def create_client() -> CustomClient:
    """Create an HTTP client for use in tests.

    Returns:
        CustomClient: A configured HTTP client instance.

    """
    return CustomClient(base_url=get_base_url(), timeout=120.0)
