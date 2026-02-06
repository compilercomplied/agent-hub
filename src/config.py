from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AnthropicConfiguration:
    """Configuration for Anthropic API.

    Attributes:
        api_key: The Anthropic API key.

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
        anthropic: Anthropic-specific configuration.

    """

    anthropic: AnthropicConfiguration


def load_configuration() -> AppConfiguration:
    """Load all application configurations from environment variables.

    Returns:
        AppConfiguration: The loaded configuration object.

    """
    return AppConfiguration(
        anthropic=AnthropicConfiguration(
            api_key=get_env_or_raise("ANTHROPIC_API_KEY"),
        ),
    )
