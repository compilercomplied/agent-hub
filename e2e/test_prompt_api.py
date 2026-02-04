"""End-to-end tests for the prompt API.

These tests follow the arrange-act-assert pattern and perform
black-box testing without importing the application code.
"""

from __future__ import annotations

import pytest

from e2e.client import create_client


class TestPromptAPI:
    """Test suite for the /api/v1/prompt endpoint."""

    def test_prompt_endpoint_returns_hello_world(self) -> None:
        """Test that the prompt endpoint returns 'hello world'.

        This test follows the arrange-act-assert pattern:
        - Arrange: Set up the HTTP client and request payload
        - Act: Make a POST request to the endpoint
        - Assert: Verify the response status and content
        """
        # Arrange
        client = create_client()
        payload = {"prompt": "test prompt"}

        # Act
        response = client.post("/api/v1/prompt", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "hello world"

        client.close()

    def test_prompt_endpoint_accepts_valid_prompt(self) -> None:
        """Test that the endpoint accepts various valid prompt strings.

        This test verifies that different types of valid prompts
        are accepted by the API.
        """
        # Arrange
        client = create_client()
        test_prompts = [
            "Simple prompt",
            "A longer prompt with multiple words and punctuation!",
            "12345",
            "Special characters: @#$%^&*()",
        ]

        for prompt in test_prompts:
            # Act
            response = client.post("/api/v1/prompt", json={"prompt": prompt})

            # Assert
            assert response.status_code == 200
            assert response.json()["message"] == "hello world"

        client.close()

    def test_prompt_endpoint_requires_prompt_field(self) -> None:
        """Test that the endpoint requires the prompt field.

        This test verifies that requests without a prompt field
        are rejected with appropriate error codes.
        """
        # Arrange
        client = create_client()
        payload = {}  # Missing prompt field

        # Act
        response = client.post("/api/v1/prompt", json=payload)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

        client.close()

    def test_prompt_endpoint_rejects_empty_prompt(self) -> None:
        """Test that the endpoint rejects empty prompt strings.

        This test verifies validation of the prompt field.
        """
        # Arrange
        client = create_client()
        payload = {"prompt": ""}

        # Act
        response = client.post("/api/v1/prompt", json=payload)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

        client.close()

    def test_prompt_endpoint_returns_json(self) -> None:
        """Test that the endpoint returns a valid JSON response.

        This test verifies the response format and content type.
        """
        # Arrange
        client = create_client()
        payload = {"prompt": "test"}

        # Act
        response = client.post("/api/v1/prompt", json=payload)

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        data = response.json()
        assert isinstance(data, dict)
        assert isinstance(data.get("message"), str)

        client.close()


class TestHealthEndpoint:
    """Test suite for the health check endpoint."""

    def test_health_endpoint_returns_healthy_status(self) -> None:
        """Test that the health endpoint returns a healthy status.

        This verifies the health check endpoint is operational.
        """
        # Arrange
        client = create_client()

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

        client.close()


@pytest.fixture(scope="session", autouse=True)
def _wait_for_api() -> None:
    """Wait for the API to be ready before running tests.

    This fixture ensures the API is available before tests execute.
    """
    import time

    client = create_client()
    max_retries = 30
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            response = client.get("/health")
            if response.status_code == 200:
                client.close()
                return
        except Exception:  # noqa: S110
            pass

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    client.close()
    msg = "API did not become ready in time"
    raise RuntimeError(msg)
