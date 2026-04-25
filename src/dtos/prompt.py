from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


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
