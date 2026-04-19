from __future__ import annotations

from pydantic import BaseModel


class K8sIntegrationResponse(BaseModel):
    """Response model for K8s integration test.

    Attributes:
        pod_name: The name of the pod created.
        status: The final status of the pod execution.

    """

    pod_name: str
    status: str
