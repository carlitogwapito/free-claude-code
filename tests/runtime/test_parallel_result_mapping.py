"""Parallel search result formats preserve the same evidence and validation."""

import json

import pytest
from free_claude_code.runtime.web_tools.client import _parallel_search_results


def envelope(payload: object, structured: bool) -> dict[str, object]:
    if structured:
        return {"result": {"structuredContent": payload}}
    return {"result": {"content": [{"type": "text", "text": json.dumps(payload)}]}}


def test_text_fallback_matches_structured_evidence_without_mutating_input() -> None:
    payload = {
        "results": [
            {"url": "https://example.com/a", "title": "Example", "excerpts": ["first", "second"]},
            {"url": "https://example.com/b", "title": None, "excerpts": ["third"]},
        ]
    }
    original = json.dumps(payload, sort_keys=True)
    structured = _parallel_search_results(envelope(payload, True))
    fallback = _parallel_search_results(envelope(payload, False))
    assert structured == fallback
    assert [(item.title, item.url, item.content) for item in structured] == [
        ("Example", "https://example.com/a", "first\nsecond"),
        ("https://example.com/b", "https://example.com/b", "third"),
    ]
    assert json.dumps(payload, sort_keys=True) == original


@pytest.mark.parametrize("structured", [True, False], ids=["structured", "text-fallback"])
def test_empty_results_are_valid_in_both_formats(structured: bool) -> None:
    assert _parallel_search_results(envelope({"results": []}, structured)) == []


@pytest.mark.parametrize(
    "response",
    [
        {"result": {"content": [{"type": "text", "text": "{not-json"}]}},
        envelope([], False),
        envelope({"results": [{"url": "https://example.com/a", "excerpts": [42]}]}, True),
    ],
    ids=["invalid-json", "non-object-text-result", "non-string-excerpt"],
)
def test_malformed_result_content_is_rejected(response: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _parallel_search_results(response)
