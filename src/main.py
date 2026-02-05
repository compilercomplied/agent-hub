"""FastAPI application for Agent Hub.

This module provides a REST API endpoint for processing prompts.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

# Filter out health check logs
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args is not None and len(record.args) >= 3 and str(record.args[2]).find("/health") == -1

# Add filter to uvicorn access logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

app = FastAPI(
    title="Agent Hub API",
    description="API for agent orchestration and prompt processing",
    version="1.0.0",
)


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
    return PromptResponse(message="hello world")


@app.get("/health", summary="Health check endpoint")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Status information.

    """
    return {"status": "healthy"}
