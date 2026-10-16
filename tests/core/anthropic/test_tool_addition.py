"""Advisor tool additions survive request parsing and public serialization."""

import pytest
from free_claude_code.core.anthropic.models import (
    ContentBlockText,
    ContentBlockToolAddition,
    MessagesRequest,
    TokenCountRequest,
)
from free_claude_code.core.anthropic.request_serialization import dump_messages_request
from pydantic import ValidationError


def test_tool_addition_round_trip_preserves_nested_fields_and_block_order() -> None:
    blocks = [
        {"type": "text", "text": "Get a second opinion."},
        {
            "type": "tool_addition",
            "tool": {
                "type": "tool_reference",
                "name": "advisor",
                "future_options": {"enabled": True, "choices": ["a", "b"]},
            },
            "cache_control": {"type": "ephemeral", "ttl": "5m"},
        },
        {"type": "text", "text": "Continue after the advice."},
    ]
    request = MessagesRequest.model_validate(
        {"model": "test-model", "messages": [{"role": "user", "content": blocks}]}
    )
    parsed = request.messages[0].content
    assert isinstance(parsed, list)
    assert isinstance(parsed[0], ContentBlockText)
    assert isinstance(parsed[1], ContentBlockToolAddition)
    assert isinstance(parsed[2], ContentBlockText)

    body = dump_messages_request(request)

    assert body["messages"][0]["content"] == blocks


def test_token_count_accepts_the_same_advisor_block() -> None:
    block = {
        "type": "tool_addition",
        "tool": {"type": "tool_reference", "name": "advisor"},
        "cache_control": {"type": "ephemeral"},
    }
    request = TokenCountRequest.model_validate(
        {"model": "test-model", "messages": [{"role": "user", "content": [block]}]}
    )
    parsed = request.messages[0].content
    assert isinstance(parsed, list)
    assert isinstance(parsed[0], ContentBlockToolAddition)
    assert parsed[0].model_dump() == block


@pytest.mark.parametrize(
    "block",
    [
        {"type": "tool_addition"},
        {"type": "tool_addition", "tool": None},
        {"type": "tool_addition", "tool": "advisor"},
        {"type": "tool_addition", "tool": []},
    ],
    ids=["missing", "null", "string", "list"],
)
def test_malformed_tool_addition_is_not_silently_accepted(
    block: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        MessagesRequest.model_validate(
            {"model": "test-model", "messages": [{"role": "user", "content": [block]}]}
        )
