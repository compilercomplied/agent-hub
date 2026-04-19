from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from typing_extensions import TypedDict

from src.tools.agent_dev_environment.toolkit import get_agent_dev_tools

if TYPE_CHECKING:
    from src.config import AppConfiguration


class AgentContext(TypedDict):
    """Context schema for the agent."""


# Using Any because the agent return type from LangChain is complex
# and varies depending on the tools and configuration used.
def create_app_agent(config: AppConfiguration) -> Any:  # noqa: ANN401
    """Create and configure the agent instance.

    Args:
        config: The application configuration.

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

    return create_agent(
        model, tools=get_agent_dev_tools(), context_schema=AgentContext
    )
