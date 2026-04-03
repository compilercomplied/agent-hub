"""Structured logging processors for Agent Hub.

An example of how the log looks like can be found in log-example.json.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structlog.types import EventDict


def preserve_log_template(
    _logger: object, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Preserve the original log template in a 'template' field.

    This processor should be placed BEFORE PositionalArgumentsFormatter
    to capture the raw template string.

    Returns:
        The updated event dictionary.

    """
    if "event" in event_dict:
        event_dict["template"] = event_dict["event"]
    return event_dict


def rename_event_to_message(
    _logger: object, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Rename the 'event' field to 'message' for the final output.

    This processor should be placed AFTER any formatting processors
    to ensure the final rendered string is renamed.

    Returns:
        The updated event dictionary.

    """
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict
