"""Session management for isolated agent environments."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from src.k8s.manager import K8sManager

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class Session:
    """Represents an isolated agent session.

    Attributes:
        pod_name: The name of the Kubernetes pod.
        base_url: The base URL for the environment API.
    """

    pod_name: str
    base_url: str


class SessionManager:
    """Manages the lifecycle of isolated agent sessions."""

    def __init__(self, k8s_manager: K8sManager) -> None:
        """Initialize the session manager.

        Args:
            k8s_manager: The Kubernetes manager instance.
        """
        self.k8s_manager = k8s_manager

    async def create_session(self) -> Session:
        """Create a new isolated session by spinning up a K8s pod.

        Returns:
            The created Session object.
        """
        logger.info("Creating new isolated session")
        self.k8s_manager.validate_config()

        port = 8080
        pod_name = self.k8s_manager.create_task(
            "Starting agent-dev-environment session",
            port=port,
        )

        try:
            self.k8s_manager.watch_task(pod_name)
            # Give the agent-dev-environment server a few seconds to fully start
            await asyncio.sleep(10)

            node_ip = self.k8s_manager.get_node_ip()
            base_url = f"http://{node_ip}:{port}"

            logger.info(
                "Session created successfully",
                pod_name=pod_name,
                base_url=base_url,
            )
            return Session(pod_name=pod_name, base_url=base_url)
        except Exception:
            logger.exception("Failed to create session", pod_name=pod_name)
            raise

    def delete_session(self, session: Session) -> None:
        """Clean up an isolated session by deleting the K8s pod.

        Args:
            session: The session to delete.
        """
        logger.info("Deleting isolated session", pod_name=session.pod_name)
        # K8sManager has a delete_task method or we use client directly
        try:
            self.k8s_manager.v1.delete_namespaced_pod(
                name=session.pod_name,
                namespace=self.k8s_manager.ns,
            )
        except Exception:
            logger.exception(
                "Failed to delete session pod",
                pod_name=session.pod_name,
            )
