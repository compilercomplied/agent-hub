"""FastAPI application for Agent Hub.

This module provides a REST API endpoint for processing prompts.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import FastAPI
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from src.config import load_configuration

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
try:
    config = load_configuration()
    logger.info("Configuration loaded successfully")
except Exception:
    logger.exception("Failed to load configuration")
    raise

app = FastAPI(
    title="Agent Hub API",
    description="API for agent orchestration and prompt processing",
    version="1.0.0",
)

# Initialize the LLM and the Agent
model = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    api_key=config.anthropic.api_key,
)
agent = create_react_agent(model, tools=[])
logger.info("Agent initialized successfully")


class PromptRequest(BaseModel):
    """Request model for prompt endpoint.

    Attributes:
        prompt: The prompt string to be processed.

    """

    prompt: Annotated[
        str,
        Field(
            description="The prompt text to process",
            min_length=1,
        ),
    ]


class PromptResponse(BaseModel):
    """Response model for prompt endpoint.

    Attributes:
        message: The response message.

    """

    message: str


@app.post(
    "/api/v1/prompt",
    response_model=PromptResponse,
    summary="Process a prompt",
    description="Accepts a prompt string and returns a response",
)
async def process_prompt(request: PromptRequest) -> PromptResponse:
    """Process a prompt request.

    Args:
        request: The prompt request containing the prompt text.

    Returns:
        PromptResponse: A response containing the message.

    """
    inputs = {"messages": [("user", request.prompt)]}
    result = await agent.ainvoke(inputs)
    # The last message in the list is the agent's response
    final_message = result["messages"][-1].content
    return PromptResponse(message=final_message)


@app.get("/health", summary="Health check endpoint")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Status information.

    """
    return {"status": "healthy"}
