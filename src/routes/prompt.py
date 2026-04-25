"""Route handlers for prompt-related endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog
from fastapi import APIRouter, Request
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.agents.factory import create_app_agent
from src.dtos.k8s import K8sIntegrationResponse
from src.dtos.prompt import PromptRequest, PromptResponse
from src.tools.agent_dev_environment.toolkit import get_agent_dev_tools

if TYPE_CHECKING:
    from src.session import SessionManager

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/api/v1/prompt",
    response_model=PromptResponse,
    summary="Process a prompt",
    description="Accepts a prompt string and returns a response",
)
async def process_prompt(
    request: PromptRequest, fastapi_request: Request
) -> PromptResponse:
    """Process a prompt request directly using the LLM.

    Args:
        request: The prompt request containing the prompt text.
        fastapi_request: The FastAPI request object.

    Returns:
        PromptResponse: A response containing the message.

    """
    config = fastapi_request.app.state.config

    model = ChatOpenAI(
        model="deepseek-chat",
        api_key=SecretStr(config.deepseek.api_key),
        base_url="https://api.deepseek.com",
    )

    response = await model.ainvoke(request.prompt)
    return PromptResponse(message=str(response.content))


@router.post(
    "/api/v1/test-k8s-integration",
    response_model=K8sIntegrationResponse,
    summary="Test K8s integration",
    description="Deploys a test container in K8s to verify integration",
)
async def test_k8s_integration(
    fastapi_request: Request,
) -> K8sIntegrationResponse:
    """Test K8s integration by utilizing the session manager.

    Args:
        fastapi_request: The FastAPI request object.

    Returns:
        K8sIntegrationResponse: Status of the integration test.

    """
    session_manager: SessionManager = fastapi_request.app.state.session_manager
    config = fastapi_request.app.state.config

    logger.info("Testing K8s integration via SessionManager")

    # 1. Create session
    session = await session_manager.create_session()

    try:
        # 2. Configure agent for session
        tools = get_agent_dev_tools(base_url=session.base_url)
        agent = create_app_agent(config, tools)

        # 3. Ask the agent to clone the repo
        repo_url = "https://github.com/compilercomplied/agent-hub.git"
        prompt = (
            f"Please clone the repository {repo_url} "
            f"into /tmp/agent-hub using the shell_run tool."
        )

        inputs: Any = {"messages": [{"role": "user", "content": prompt}]}
        result = await agent.ainvoke(inputs)
        agent_response = result["messages"][-1].content

        logger.info("Agent integration test completed", response=agent_response)
        return K8sIntegrationResponse(
            pod_name=session.pod_name,
            status=f"succeeded: {agent_response}",
        )
    except Exception as e:
        logger.exception(
            "K8s integration test failed",
            pod=session.pod_name,
        )
        return K8sIntegrationResponse(
            pod_name=session.pod_name,
            status=f"failed: {e}",
        )
    finally:
        # 4. Cleanup session
        session_manager.delete_session(session)
