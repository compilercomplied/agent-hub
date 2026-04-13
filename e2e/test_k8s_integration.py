"""End-to-end tests for the K8s integration API.

These tests verify the Kubernetes integration endpoint.
"""

from __future__ import annotations

from e2e.client import create_client


class TestK8sIntegrationAPI:
    """Test suite for the /api/v1/test-k8s-integration endpoint."""

    @staticmethod
    def test_k8s_integration_endpoint_returns_status() -> None:
        """Test that the K8s integration endpoint returns a valid response.

        Since we might be running with a dummy kubeconfig, we check
        that the response contains the expected fields.
        """
        # Arrange
        client = create_client()

        # Act
        response = client.post("/api/v1/test-k8s-integration")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "pod_name" in data
        assert "status" in data
        # We don't assert "succeeded" because it might fail with dummy config
        assert isinstance(data["pod_name"], str)
        assert isinstance(data["status"], str)

        client.close()
