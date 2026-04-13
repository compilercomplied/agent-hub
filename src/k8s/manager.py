"""Kubernetes manager for deploying and watching agent pods."""

from __future__ import annotations

import base64
import hashlib
import os
import time
from typing import TYPE_CHECKING, cast

import structlog
import yaml
from kubernetes import client, config, watch

if TYPE_CHECKING:
    from typing import Any

    from src.config import K8sConfiguration

logger = structlog.get_logger(__name__)


class K8sManager:
    """Manages Kubernetes pod lifecycle for agents."""

    def __init__(self, cfg: K8sConfiguration) -> None:
        """Initialize the Kubernetes manager.

        Args:
            cfg: Kubernetes configuration.

        """
        self.namespace = "agents"
        self.timeout = 120
        self.image = "ghcr.io/compilercomplied/agent-dev-environment"

        # Load kubeconfig from base64 string
        try:
            kubeconfig_dict = yaml.safe_load(
                base64.b64decode(cfg.kubeconfig_base64).decode("utf-8")
            )
            config.load_kube_config_from_dict(kubeconfig_dict)
            self.core_v1 = client.CoreV1Api()
            logger.info("Kubernetes client initialized successfully")
        except Exception:
            logger.exception("Failed to initialize Kubernetes client")
            raise

    @staticmethod
    def generate_pod_name(task: str) -> str:
        """Generate a unique pod name based on the task content.

        Args:
            task: The task description.

        Returns:
            str: A unique pod name.

        """
        task_hash = hashlib.sha256(task.encode("utf-8")).hexdigest()[:10]
        rand_suffix = os.urandom(3).hex()
        return f"agent-{task_hash}-{rand_suffix}"

    def create_task(self, task: str) -> str:
        """Create an agent pod and return its name.

        Args:
            task: The task for the agent to perform.

        Returns:
            str: The name of the created pod.

        """
        pod_name = self.generate_pod_name(task)
        logger.info("Starting agent in k8s", pod=pod_name, task_len=len(task))

        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_name,
                labels={
                    "app": "agent-worker",
                    "app.kubernetes.io/managed-by": "agent-orchestrator",
                },
            ),
            spec=client.V1PodSpec(
                restart_policy="Never",
                image_pull_secrets=[
                    client.V1LocalObjectReference(name="ghcr-secret-cddca01f")
                ],
                containers=[
                    client.V1Container(
                        name="agent-worker",
                        image=self.image,
                        args=["--dangerously-skip-permissions", task],
                        env_from=[
                            client.V1EnvFromSource(
                                secret_ref=client.V1SecretEnvSource(
                                    name="dev-environment-secrets"
                                )
                            )
                        ],
                    )
                ],
            ),
        )

        try:
            self.core_v1.create_namespaced_pod(
                namespace=self.namespace,
                body=pod,
            )
        except Exception:
            logger.exception("Failed to create pod", pod=pod_name)
            raise
        else:
            return pod_name

    def watch_task(self, pod_name: str) -> None:
        """Wait for the specified pod to complete.

        Args:
            pod_name: The name of the pod to watch.

        Raises:
            RuntimeError: If the pod fails or times out.

        """
        logger.info("Waiting for pod to complete...", pod=pod_name)
        w = watch.Watch()
        start_time = time.time()
        failed = False

        try:
            for event in w.stream(
                self.core_v1.list_namespaced_pod,
                namespace=self.namespace,
                field_selector=f"metadata.name={pod_name}",
                timeout_seconds=self.timeout,
            ):
                if not event:
                    continue
                # event is a dict containing 'type' and 'object'
                # w.stream returns an Any generator
                ev = cast("dict[str, Any]", event)
                pod = cast("client.V1Pod", ev["object"])
                if pod.status is None:
                    continue
                phase = pod.status.phase

                if phase == "Succeeded":
                    logger.info("Pod succeeded", pod=pod_name)
                    return
                if phase == "Failed":
                    logger.error("Pod failed", pod=pod_name)
                    failed = True
                    break

                if time.time() - start_time > self.timeout:
                    break
        except Exception:
            logger.exception("Error watching pod", pod=pod_name)
            raise

        if failed:
            msg = f"Pod {pod_name} failed"
            raise RuntimeError(msg)

        msg = f"Timeout waiting for pod {pod_name} execution"
        raise RuntimeError(msg)

    def validate_config(self) -> None:
        """Validate the Kubernetes connection.

        This lists pods in the namespace to verify connectivity.

        """
        try:
            self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                limit=1,
            )
            logger.info("Kubernetes connection validated")
        except Exception:
            logger.exception("Failed to validate k8s connection")
            raise
