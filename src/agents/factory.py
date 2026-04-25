"""Agent factory for creating LangChain agents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

    from src.config import AppConfiguration


class AgentContext(TypedDict):
    """Context schema for the agent."""


def create_app_agent(
    config: AppConfiguration,
    tools: list[BaseTool],
) -> Any:  # noqa: ANN401
    """Create and configure the agent instance with specific tools.

    Args:
        config: The application configuration.
        tools: The list of tools the agent can use.

    Returns:
        The configured agent instance.
    """
    model = ChatOpenAI(
        model="deepseek-chat",
        api_key=SecretStr(config.deepseek.api_key),
        base_url="https://api.deepseek.com",
        timeout=30,
        max_retries=5,
    )

    system_prompt = (
        "You are a helpful coding assistant with access to a "
        "development environment. "
        "You can run shell commands and list files using the provided "
        "tools to perform tasks. "
        "When asked to write code, clone repositories, or examine files, "
        "use your tools appropriately. "
        "You do NOT need to ask for a URL; the environment is already "
        "configured for you."
    )

    return create_agent(
        model,
        tools=tools,
        context_schema=AgentContext,
        system_prompt=system_prompt,
    )
