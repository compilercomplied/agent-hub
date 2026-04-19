"""Toolkit for agent development environment operations."""

from __future__ import annotations

from typing import Any, cast, override

from gdariodev_agent_dev_environment import ApiClient, Configuration, DefaultApi

# Import from the specific modules to avoid reportPrivateImportUsage
from gdariodev_agent_dev_environment.models.agent_dev_environment_src_api_v1_filesystem_ls_request import (  # noqa: E501
    AgentDevEnvironmentSrcApiV1FilesystemLsRequest,
)
from gdariodev_agent_dev_environment.models.agent_dev_environment_src_api_v1_shell_run_request import (  # noqa: E501
    AgentDevEnvironmentSrcApiV1ShellRunRequest,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class ShellRunInput(BaseModel):
    """Input for ShellRunTool."""

    command: str = Field(description="The shell command to run")
    base_url: str = Field(
        description="The base URL of the agent-dev-environment server",
    )


class ShellRunTool(BaseTool):
    """Tool that runs a shell command in the agent-dev-environment."""

    name: str = "shell_run"
    description: str = "Run a shell command in the agent-dev-environment"
    # Use cast to satisfy invariant type requirements of BaseTool
    args_schema: type[BaseModel] = cast("type[BaseModel]", ShellRunInput)  # type: ignore [reportIncompatibleVariableOverride]

    @override
    def _run(self, command: str, base_url: str) -> str:
        """Execute the tool.

        Args:
            command: The command to run.
            base_url: The base URL of the environment server.

        Returns:
            The output of the command.
        """
        config = Configuration(host=base_url)
        with ApiClient(config) as api_client:
            api_instance = DefaultApi(api_client)
            request = AgentDevEnvironmentSrcApiV1ShellRunRequest(
                command=command,
            )
            try:
                response = cast(
                    "Any", api_instance.api_v1_shell_run_post(request)
                )
                return str(response.command_output)
            except Exception as e:  # noqa: BLE001
                return f"Error running command: {e}"


class FilesystemLsInput(BaseModel):
    """Input for FilesystemLsTool."""

    path: str = Field(description="The directory path to list")
    base_url: str = Field(
        description="The base URL of the agent-dev-environment server",
    )


class FilesystemLsTool(BaseTool):
    """Tool that lists files in a directory in the agent-dev-environment."""

    name: str = "filesystem_ls"
    description: str = "List files in a directory in the agent-dev-environment"
    # Use cast to satisfy invariant type requirements of BaseTool
    args_schema: type[BaseModel] = cast("type[BaseModel]", FilesystemLsInput)  # type: ignore [reportIncompatibleVariableOverride]

    @override
    def _run(self, path: str, base_url: str) -> str:
        """Execute the tool.

        Args:
            path: The path to list.
            base_url: The base URL of the environment server.

        Returns:
            The list of directory entries.
        """
        config = Configuration(host=base_url)
        with ApiClient(config) as api_client:
            api_instance = DefaultApi(api_client)
            request = AgentDevEnvironmentSrcApiV1FilesystemLsRequest(path=path)
            try:
                response = cast(
                    "Any", api_instance.api_v1_filesystem_ls_post(request)
                )
                return str(response.command_output)
            except Exception as e:  # noqa: BLE001
                return f"Error listing directory: {e}"


def get_agent_dev_tools() -> list[BaseTool]:
    """Return the list of agent dev tools.

    Returns:
        A list of BaseTool instances.
    """
    return [ShellRunTool(), FilesystemLsTool()]
