from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class KimiConfiguration:
    """Configuration for Kimi API.

    Attributes:
        api_key: The Kimi API key.

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
class AppConfiguration:
    """Centralized application configuration.

    Attributes:
        kimi: Kimi-specific configuration.
        logging: Logging configuration.

    """

    kimi: KimiConfiguration
    logging: LoggingConfiguration


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
        kimi=KimiConfiguration(
            api_key=get_env_or_raise("KIMI_API_KEY"),
        ),
        logging=LoggingConfiguration(
            type=logging_type,  # type: ignore[arg-type]
        ),
    )
