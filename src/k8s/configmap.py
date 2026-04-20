"""Configuration manager for the Agent Development Environment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

import structlog

if TYPE_CHECKING:
    from kubernetes import client

logger = structlog.get_logger(__name__)


class ConfigMapError(Exception):
    """Exception raised for errors in loading config from the ConfigMap."""


@dataclass(frozen=True)
class AgentDevEnvConfig:
    """Configuration for the Agent Development Environment."""

    image: str
    env_vars: list[dict[str, str]]


def load_agent_dev_env_config(
    v1_client: client.CoreV1Api,
    namespace: str,
    overrides: dict[str, str] | None,
    port: int,
) -> AgentDevEnvConfig:
    """Load config from the configmap and merge it with overrides and port.

    Args:
        v1_client: The Kubernetes CoreV1Api client.
        namespace: The namespace where the configmap resides.
        overrides: Optional runtime environment variable overrides.
        port: The randomized port the agent should listen on.

    Returns:
        The merged AgentDevEnvConfig.

    Raises:
        ConfigMapError: If the configmap is missing or malformed.
    """
    cm_name = "agent-dev-environment-configmap"
    try:
        cm = cast(
            "Any", v1_client.read_namespaced_config_map(cm_name, namespace)
        )
    except Exception as e:
        msg = f"Failed to read ConfigMap '{cm_name}' in namespace '{namespace}'"
        raise ConfigMapError(msg) from e

    if not cm or not getattr(cm, "data", None):
        msg = f"ConfigMap '{cm_name}' is missing or empty"
        raise ConfigMapError(msg)

    # Use a fixed default image since templates aren't in the ConfigMap
    image = "ghcr.io/compilercomplied/agent-dev-environment:latest"

    # Build merged environment
    env_dict: dict[str, str] = {}

    # 1. Base environment from ConfigMap data
    for k, v in cm.data.items():
        env_dict[k] = str(v)

    # 2. Runtime overrides (takes precedence over ConfigMap)
    if overrides:
        for k, v in overrides.items():
            env_dict[k] = str(v)

    # 3. Mandatory port override (takes highest precedence)
    env_dict["AGENT_DEV_ENVIRONMENT_PORT"] = str(port)

    # Convert to list of dicts for kubernetes
    env_vars = [{"name": k, "value": v} for k, v in env_dict.items()]

    logger.info(
        "Loaded and merged agent configuration",
        image=image,
        port=port,
        env_count=len(env_vars),
    )

    return AgentDevEnvConfig(image=image, env_vars=env_vars)
