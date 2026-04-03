from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KimiConfiguration:
    """Configuration for Kimi API.

    Attributes:
        api_key: The Kimi API key.

    """

    api_key: str


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
class AppConfiguration:
    """Centralized application configuration.

    Attributes:
        kimi: Kimi-specific configuration.

    """

    kimi: KimiConfiguration


def load_configuration() -> AppConfiguration:
    """Load all application configurations from environment variables.

    Returns:
        AppConfiguration: The loaded configuration object.

    """
    return AppConfiguration(
        kimi=KimiConfiguration(
            api_key=get_env_or_raise("KIMI_API_KEY"),
        ),
    )
