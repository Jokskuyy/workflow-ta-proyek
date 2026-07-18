"""Property-based tests for the ListFormatter of the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers task 4.2 (Property 7) against the PURE ListFormatter helpers exposed by
``skills/scripts/alur_penulisan/list_formatter.py``:

  render_list, marker_for_level, clamp_level

The rendering logic is pure (tree-in / lines-out), so 100+ Hypothesis
iterations over randomly nested ``ListNode`` trees — including trees deeper than
4 levels — are cheap. This is a brand-new file; no existing test is modified.
"""
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the ListFormatter from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.list_formatter import (  # noqa: E402
    LIST_INDENT_UNIT,
    render_list,
)
from alur_penulisan.models import ListNode  # noqa: E402

# Deepest level with a distinct marker; deeper items reuse the level-4 marker.
MAX_LIST_LEVEL = 4


# --------------------------------------------------------------------------- #
# Independent reference implementation of the numbering rules (from design.md
# Requirements 3.1–3.4). Deriving expectations independently — rather than
# calling the implementation's own marker_for_level — keeps this a genuine
# correctness check rather than a tautology.
# --------------------------------------------------------------------------- #
def _ref_alpha(index: int) -> str:
    """Spreadsheet-style lowercase label: 0->'a', 25->'z', 26->'aa'."""
    if index < 0:
        index = 0
    label = ""
    n = index
    while True:
        label = chr(ord("a") + (n % 26)) + label
        n = n // 26 - 1
        if n < 0:
            break
    return label


def _ref_marker(level: int, index: int) -> str:
    """Expected marker for a (possibly out-of-range) level and 0-based sibling index.

    Rule (Requirement 3.1 + 3.4): level 1 -> ``N.``, level 2 -> ``x.``,
    level 3 -> ``N)``, level 4 (and any deeper, clamped) -> ``x)``.
    Rule (Requirement 3.2 + 3.3): the sequential value is ``index + 1`` (numeric)
    or the ``index``-th alphabetic label, always starting at 0 for the first
    sibling of a fresh (sub-)level.
    """
    lvl = level
    if lvl < 1:
        lvl = 1
    if lvl > MAX_LIST_LEVEL:
        lvl = MAX_LIST_LEVEL
    symbol = str(index + 1) if lvl in (1, 3) else _ref_alpha(index)
    suffix = "." if lvl in (1, 2) else ")"
    return f"{symbol}{suffix}"


def _expected_lines(nodes: list[ListNode], level: int) -> list[str]:
    """Reference rendering: pre-order, siblings reset to index 0 per (sub-)level."""
    lines: list[str] = []
    indent = " " * (LIST_INDENT_UNIT * (level - 1))
    for index, node in enumerate(nodes):
        lines.append(f"{indent}{_ref_marker(level, index)} {node.text}")
        if node.children:
            lines.extend(_expected_lines(node.children, level + 1))
    return lines


def _max_depth(nodes: list[ListNode], level: int = 1) -> int:
    depth = level if nodes else level - 1
    for node in nodes:
        if node.children:
            depth = max(depth, _max_depth(node.children, level + 1))
    return depth


# --------------------------------------------------------------------------- #
# Strategy: random nested ListNode forests, sometimes deeper than 4 levels.
# --------------------------------------------------------------------------- #
_TEXT = st.text(
    alphabet=st.characters(
        min_codepoint=0x20,
        max_codepoint=0x7E,
        blacklist_characters="\n\r",
    ),
    min_size=1,
    max_size=6,
)


@st.composite
def list_forest(draw, max_depth: int = 6, max_children: int = 4):
    """Build a forest of ListNode trees with depth up to ``max_depth`` (>4)."""

    def build_nodes(depth: int) -> list[ListNode]:
        count = draw(st.integers(min_value=1, max_value=max_children))
        nodes: list[ListNode] = []
        for _ in range(count):
            text = draw(_TEXT)
            if depth < max_depth and draw(st.booleans()):
                children = build_nodes(depth + 1)
            else:
                children = []
            nodes.append(ListNode(text=text, children=children))
        return nodes

    return build_nodes(1)


# Feature: automated-writing-workflow, Property 7: Kebenaran penomoran Daftar_Berjenjang
@settings(max_examples=100)
@given(forest=list_forest())
def test_property_7_daftar_berjenjang_numbering(forest):
    """Property 7: Kebenaran penomoran Daftar_Berjenjang.

    Validates: Requirements 3.1, 3.2, 3.3, 3.4
    """
    rendered = render_list(forest)

    # Rule 3.1–3.4 combined: rendered output matches the independent reference
    # (correct marker style per level, sequential +1 siblings from 1/a, each
    # sub-level reset to the initial marker, depth >4 pinned to level-4 style).
    assert rendered == _expected_lines(forest, 1)

    # Rule 3.4 (explicit): every item deeper than level 4 keeps the level-4
    # marker style — an alphabetic label followed by ')'.
    def _check_deep(nodes: list[ListNode], level: int) -> None:
        for index, node in enumerate(nodes):
            if level > MAX_LIST_LEVEL:
                expected = f"{_ref_alpha(index)})"
                indent = " " * (LIST_INDENT_UNIT * (level - 1))
                assert f"{indent}{expected} {node.text}" in rendered
            if node.children:
                _check_deep(node.children, level + 1)

    _check_deep(forest, 1)
