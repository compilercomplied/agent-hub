from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, Any

import structlog
from fastapi import APIRouter, Request

from src.dtos.k8s import K8sIntegrationResponse
from src.dtos.prompt import PromptRequest, PromptResponse

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

    """Process a prompt request.

    Args:
        request: The prompt request containing the prompt text.
        fastapi_request: The FastAPI request object.

    Returns:
        PromptResponse: A response containing the message.

    """
    agent = fastapi_request.app.state.agent
    # Use Any to satisfy complex library-defined type requirements for ainvoke
    inputs: Any = {"messages": [{"role": "user", "content": request.prompt}]}
    result = await agent.ainvoke(inputs)
    # The last message in the list is the agent's response
    final_message = result["messages"][-1].content
    return PromptResponse(message=str(final_message))


@router.post(
    "/api/v1/test-k8s-integration",
    response_model=K8sIntegrationResponse,
    summary="Test K8s integration",
    description="Deploys a test container in K8s to verify integration",
)
async def test_k8s_integration(
    fastapi_request: Request,
) -> K8sIntegrationResponse:
    """Test K8s integration by deploying a dummy pod.

    Deploys a test container and uses the agent to clone this repo.

    Args:
        fastapi_request: The FastAPI request object.

    Returns:
        K8sIntegrationResponse: Status of the integration test.

    """
    agent = fastapi_request.app.state.agent
    k8s_manager = fastapi_request.app.state.k8s_manager

    logger.info("Testing K8s integration")
    k8s_manager.validate_config()

    # The agent-dev-environment image starts a server.
    # Randomize port for hostNetwork: True
    random_port = random.randint(10000, 20000)  # noqa: S311
    pod_name = k8s_manager.create_task(
        "echo 'Starting agent-dev-environment'", port=random_port
    )

    try:
        k8s_manager.watch_task(pod_name)
        # Give the agent-dev-environment server a few seconds to fully start
        await asyncio.sleep(10)
        node_ip = k8s_manager.get_node_ip()
        base_url = f"http://{node_ip}:{random_port}"

        # Ask the agent to clone the repo
        repo_url = "https://github.com/compilercomplied/agent-hub.git"
        prompt = (
            f"Please clone the repository {repo_url} "
            f"into /tmp/agent-hub using the shell_run tool. "
            f"The base_url is {base_url}."
        )

        inputs: Any = {"messages": [{"role": "user", "content": prompt}]}
        result = await agent.ainvoke(inputs)
        agent_response = result["messages"][-1].content

        logger.info("Agent integration test completed", response=agent_response)
        return K8sIntegrationResponse(
            pod_name=pod_name, status=f"succeeded: {agent_response}"
        )
    except RuntimeError as e:
        logger.exception("K8s integration test failed", pod=pod_name)
        return K8sIntegrationResponse(pod_name=pod_name, status=f"failed: {e}")
