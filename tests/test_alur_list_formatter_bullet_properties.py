"""Property-based test for the ListFormatter bullet-marker prohibition.

Spec: .kiro/specs/automated-writing-workflow

Covers task 4.3 (Property 8) against the PURE ListFormatter renderer exposed by
``skills/scripts/alur_penulisan/list_formatter.py`` (``render_list``).

Property 8 states that for every list written to Berkas_Draf, no item at any
level uses a bullet marker (``-``, ``*``, or ``+``). The renderer is pure
(tree-in / lines-out), so 100+ Hypothesis iterations over randomly nested
``ListNode`` forests — including forests deeper than 4 levels and text that
itself contains bullet characters — are cheap. This is a brand-new file; no
existing test is modified.
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

from alur_penulisan.list_formatter import render_list  # noqa: E402
from alur_penulisan.models import ListNode  # noqa: E402

BULLET_MARKERS = {"-", "*", "+"}


# --------------------------------------------------------------------------- #
# Strategy: random nested ListNode forests, sometimes deeper than 4 levels.
# Text deliberately allows bullet characters so we prove the ban applies to the
# *marker*, not to legitimate content that happens to contain '-', '*', or '+'.
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


def _marker_of(line: str) -> str:
    """Extract the list marker from a rendered line ``<indent><marker> <text>``."""
    stripped = line.lstrip(" ")
    # The marker is the first whitespace-delimited token.
    return stripped.split(" ", 1)[0]


# Feature: automated-writing-workflow, Property 8: Tidak ada penanda bullet
@settings(max_examples=100)
@given(forest=list_forest())
def test_property_8_no_bullet_markers(forest):
    """Property 8: Tidak ada penanda bullet.

    Validates: Requirements 3.5
    """
    rendered = render_list(forest)

    for line in rendered:
        marker = _marker_of(line)
        # The marker itself must never be a bullet symbol...
        assert marker not in BULLET_MARKERS, (
            f"bullet marker {marker!r} found in line {line!r}"
        )
        # ...nor may it begin with one (defensive against any bullet+suffix form).
        assert marker[:1] not in BULLET_MARKERS, (
            f"line {line!r} starts with a bullet marker"
        )
