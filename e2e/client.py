"""HTTP client configuration for e2e tests.

This module provides the HTTP client setup for black-box testing
of the API without importing the application code.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from collections.abc import Generator


def get_base_url() -> str:
    """Get the base URL for the API.

    Returns:
        str: The base URL from environment variable or default.

    """
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


def get_client() -> Generator[httpx.Client, None, None]:
    """Get an HTTP client configured for the API.

    Yields:
        httpx.Client: A configured HTTP client instance.

    """
    base_url = get_base_url()
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        yield client


def create_client() -> httpx.Client:
    """Create an HTTP client for use in tests.

    Returns:
        httpx.Client: A configured HTTP client instance.

    """
    return httpx.Client(base_url=get_base_url(), timeout=30.0)
