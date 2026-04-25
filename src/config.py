from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DeepSeekConfiguration:
    """Configuration for DeepSeek API.

    Attributes:
        api_key: The DeepSeek API key.

    """

    api_key: str


@dataclass(frozen=True)
class LoggingConfiguration:
    """Configuration for logging.

    Attributes:
        type: The logging type (plain or structured).

    """

    type: Literal["plain", "structured"]


class ConfigurationError(Exception):
    """Exception raised when a configuration value is missing."""


def get_env_or_raise(key: str) -> str:
    """Get an environment variable or raise an error if not found.

    Args:
        key: The environment variable key (without prefix).

    Returns:
        str: The environment variable value.

    Raises:
        ConfigurationError: If the environment variable is not set.

    """
    prefix = "AGENT_HUB_"
    full_key = f"{prefix}{key}"
    value = os.getenv(full_key)
    if not value:
        msg = f"Missing mandatory environment variable: {full_key}"
        raise ConfigurationError(msg)
    return value


@dataclass(frozen=True)
class K8sConfiguration:
    """Configuration for Kubernetes integration.

    Attributes:
        kubeconfig_base64: The base64-encoded kubeconfig.

    """

    kubeconfig_base64: str


@dataclass(frozen=True)
class AppConfiguration:
    """Centralized application configuration.

    Attributes:
        deepseek: DeepSeek-specific configuration.
        logging: Logging configuration.
        k8s: Kubernetes configuration.

    """

    deepseek: DeepSeekConfiguration
    logging: LoggingConfiguration
    k8s: K8sConfiguration


def load_configuration() -> AppConfiguration:
    """Load all application configurations from environment variables.

    Returns:
        AppConfiguration: The loaded configuration object.

    Raises:
        ConfigurationError: If a mandatory environment variable is missing or
        invalid.

    """
    logging_type = get_env_or_raise("LOGGING_TYPE")
    if logging_type not in {"plain", "structured"}:
        msg = (f"Invalid value for AGENT_HUB_LOGGING_TYPE: {logging_type}."
             " Expected 'plain' or 'structured'.")
        raise ConfigurationError(msg)

    return AppConfiguration(
        deepseek=DeepSeekConfiguration(
            api_key=get_env_or_raise("DEEPSEEK_API_KEY"),
        ),
        logging=LoggingConfiguration(
            type=logging_type,  # type: ignore[arg-type]
        ),
        k8s=K8sConfiguration(
            kubeconfig_base64=get_env_or_raise("KUBECONFIG_BASE64"),
        ),
    )
