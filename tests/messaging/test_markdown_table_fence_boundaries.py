# SPDX-License-Identifier: AGPL-3.0-only
"""Focused normalizer boundaries, without loading an app or platform renderer."""

import importlib.util
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[2]
    / "src/free_claude_code/messaging/rendering/markdown_tables.py"
)
SPEC = importlib.util.spec_from_file_location("isolated_fence_policy", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
NORMALIZE = MODULE.normalize_gfm_tables
TABLE = "| A | B |\n| --- | --- |"


def test_backtick_info_with_backtick_is_not_a_fence():
    prefix = "```lang`invalid"
    text = f"{prefix}\n{TABLE}"
    expected = f"{prefix}\n\n{TABLE}"

    result = NORMALIZE(text)

    print(f"invalid backtick info -> {result!r}")
    assert result == expected
    assert NORMALIZE(result) == result


def test_tilde_info_can_contain_backticks():
    text = f"~~~lang`allowed\nexample\n{TABLE}\n~~~"

    result = NORMALIZE(text)

    print(f"valid tilde info -> {result!r}")
    assert result == text
    assert NORMALIZE(result) == result


def test_marker_and_length_reset_between_blocks():
    first = f"~~~~~python\nfirst\n{TABLE}\n~~~~~~"
    second = f"```python\nsecond\n{TABLE}\n````\t"
    third = f"~~~python\nthird\n{TABLE}\n~~~"
    text = f"{first}\n{TABLE}\n{second}\n{TABLE}\n{third}\n{TABLE}"
    expected = f"{first}\n\n{TABLE}\n{second}\n\n{TABLE}\n{third}\n\n{TABLE}"

    result = NORMALIZE(text)

    print(f"successive fence states -> {result!r}")
    assert result == expected
    assert result.count("\n\n") == 3
    assert NORMALIZE(result) == result
