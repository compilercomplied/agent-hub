"""Simplified Kubernetes manager for agent tasks."""

from __future__ import annotations

import base64
import os
import time
from typing import TYPE_CHECKING, Any, cast

import structlog
import yaml
from kubernetes import client, config

from src.k8s.configmap import load_agent_dev_env_config

if TYPE_CHECKING:
    from src.config import K8sConfiguration


logger = structlog.get_logger(__name__)


class K8sManagerError(Exception):
    """Custom exception for K8sManager errors."""


class K8sManager:
    """Manager for Kubernetes operations related to agent tasks."""

    def __init__(self, cfg: K8sConfiguration) -> None:
        """Initialize K8s client from base64 kubeconfig.

        Args:
            cfg: The K8s configuration.
        """
        self.ns = "agents"
        # Initialize K8s client from base64 kubeconfig
        k_dict = yaml.safe_load(base64.b64decode(cfg.kubeconfig_base64))
        config.load_kube_config_from_dict(k_dict)
        self.v1 = client.CoreV1Api()

    def create_task(
        self,
        _task: str,
        overrides: dict[str, str] | None = None,
        port: int = 8080,
    ) -> str:
        """Create and deploy a new agent task pod.

        Args:
            _task: The task description (currently unused).
            overrides: Optional environment variable overrides.
            port: The port the agent should listen on.

        Returns:
            The name of the created pod.
        """
        # 1. Fetch the config and merged environment variables
        env_config = load_agent_dev_env_config(
            self.v1, self.ns, overrides, port
        )
        image = env_config.image

        # 2. Prepare the pod manifest
        name = f"agent-{os.urandom(4).hex()}"
        logger.info("Deploying agent task", pod=name, image=image, port=port)

        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": name, "labels": {"app": "agent-worker"}},
            "spec": {
                "restartPolicy": "Never",
                "hostNetwork": True,
                "imagePullSecrets": [{"name": "ghcr-secret-867576aa"}],
                "containers": [{
                    "name": "worker",
                    "image": image,
                    "env": env_config.env_vars,
                    "envFrom": [
                        {"secretRef": {"name": "agent-dev-environment-secret"}},
                    ],
                }],
            },
        }

        self.v1.create_namespaced_pod(namespace=self.ns, body=pod_manifest)
        return name

    def watch_task(self, name: str, timeout: int = 120) -> None:
        """Wait for a pod to reach the Running phase.

        Args:
            name: The name of the pod to watch.
            timeout: Maximum time to wait in seconds.

        Raises:
            RuntimeError: If the pod fails or times out.
        """
        start = time.time()
        while time.time() - start < timeout:
            status_obj = cast(
                "Any", self.v1.read_namespaced_pod_status(name, self.ns)
            )
            status = status_obj.status.phase
            if status == "Running":
                return
            if status == "Failed":
                msg = f"Pod {name} failed"
                raise RuntimeError(msg)
            time.sleep(2)
        msg = f"Timeout waiting for {name} to reach Running phase"
        raise RuntimeError(msg)

    def get_pod_ip(self, name: str) -> str:
        """Get the IP address of a given pod.

        Args:
            name: The name of the pod.

        Returns:
            The pod's IP address.

        Raises:
            K8sManagerError: If the pod has no IP.
        """
        pod = cast("Any", self.v1.read_namespaced_pod(name, self.ns))
        ip = pod.status.pod_ip
        if not ip:
            msg = f"Pod {name} has no IP"
            raise K8sManagerError(msg)
        return ip

    def get_node_ip(self) -> str:
        """Get the internal IP address of the first node.

        Returns:
            The node's internal IP address.

        Raises:
            RuntimeError: If no nodes or no internal IP are found.
        """
        nodes = self.v1.list_node().items
        if not nodes:
            msg = "No nodes found"
            raise RuntimeError(msg)
        # Find InternalIP in the first node's addresses
        for addr in nodes[0].status.addresses:
            if addr.type == "InternalIP":
                return addr.address
        msg = "No InternalIP found on node"
        raise RuntimeError(msg)

    def validate_config(self) -> None:
        """Validate the K8s configuration by listing pods.

        Raises:
            RuntimeError: If listing pods fails.
        """
        try:
            self.v1.list_namespaced_pod(self.ns, limit=1)
        except Exception as e:
            msg = f"K8s configuration validation failed: {e}"
            raise RuntimeError(msg) from e
