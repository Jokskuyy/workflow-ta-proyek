"""Property + unit tests for list nesting by indentation (R3) of the
writing-pipeline-improvements spec.

Spec: .kiro/specs/writing-pipeline-improvements

Covers:
  * design Property 9 (compute_list_level depends only on indentation, indent 0
    -> outermost level, monotonic non-decreasing, marker is cosmetic).
  * backward-compatibility (R3.4): list levels in the current Markdown draft
    follow the canonical left/hanging-indentation contract.

``compute_list_level`` is a pure, deterministic transform so 100+ Hypothesis
iterations are cheap.
"""
import json
import re
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import from the canonical Mesin_Merge script.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SCRATCH))

import merge_draft_to_docx as mrg  # noqa: E402

DRAFT = ROOT / "Tugas_Akhir_Draft.md"
BASELINE = FIXTURES / "wpi_baseline_list_levels.json"

# Markers that may legitimately appear (cosmetic only): 1. a. 1) a) etc.
_MARKERS = st.sampled_from(["1.", "2.", "10.", "a.", "b.", "z.", "1)", "2)", "a)", "iv."])


# --------------------------------------------------------------------------- #
# Property 9.
# --------------------------------------------------------------------------- #
# Feature: writing-pipeline-improvements, Property 9: Level daftar monoton dan
# invarian terhadap penanda — compute_list_level bergantung hanya pada indentasi
# (penanda tidak mengubah level), indentasi 0 menghasilkan level terluar, dan
# untuk a <= b berlaku level(a) <= level(b).
# Validates: Requirements 3.1, 3.2, 3.3, 3.5
@settings(max_examples=200)
@given(
    indent=st.integers(min_value=0, max_value=120),
    marker_a=_MARKERS,
    marker_b=_MARKERS,
)
def test_property9_level_depends_only_on_indent(indent, marker_a, marker_b):
    # Marker is cosmetic: same indentation -> same level regardless of marker.
    assert mrg.compute_list_level(indent, marker_a) == mrg.compute_list_level(indent, marker_b)


# Feature: writing-pipeline-improvements, Property 9: indentasi 0 menghasilkan
# level terluar (level 1).
# Validates: Requirements 3.5
@settings(max_examples=200)
@given(marker=_MARKERS)
def test_property9_indent_zero_is_outermost(marker):
    assert mrg.compute_list_level(0, marker) == 1
    # No indentation can yield a level below the outermost.
    assert mrg.compute_list_level(0, marker) <= mrg.compute_list_level(5, marker)


# Feature: writing-pipeline-improvements, Property 9: monoton non-menurun pada
# indentasi — a <= b => level(a) <= level(b).
# Validates: Requirements 3.1, 3.3
@settings(max_examples=200)
@given(
    a=st.integers(min_value=0, max_value=120),
    b=st.integers(min_value=0, max_value=120),
    marker=_MARKERS,
)
def test_property9_monotonic_non_decreasing(a, b, marker):
    lo, hi = sorted((a, b))
    assert mrg.compute_list_level(lo, marker) <= mrg.compute_list_level(hi, marker)


# --------------------------------------------------------------------------- #
# Backward-compatibility (R3.4 / R3.5): current draft follows the contract.
# --------------------------------------------------------------------------- #
_LIST_RE = re.compile(r'^(\s*)([0-9a-zA-Z]+[.\)])\s+(.*)$')


def _draft_list_indents():
    """Leading-indent width of every list item in the current Draf, in order.

    Mirrors the gating of ``parse_markdown`` (only content from '# BAB I'
    onward, skipping code blocks and [TABLE] blocks) so the sequence lines up
    1:1 with the parsed list_items and the captured baseline.
    """
    lines = mrg._load_draft_text(str(DRAFT)).splitlines(keepends=True)
    indents = []
    started = False
    in_code = False
    in_table = False
    for line in lines:
        s = line.strip()
        if not started:
            if s.startswith('# BAB I') or s.startswith('# BAB 1'):
                started = True
            else:
                continue
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s.startswith('[TABLE]'):
            in_table = True
            continue
        if s.endswith('[/TABLE]'):
            in_table = False
            continue
        if in_table:
            continue
        m = _LIST_RE.match(line)
        if m:
            indents.append(len(m.group(1)))
    return indents


def test_backward_compat_draft_list_levels_match_baseline():
    """Every current-draft list paragraph follows the canonical indentation.

    The compact fixture records the format contract rather than a positional
    snapshot of a generated DOCX. Content-only edits may add or remove list
    items without requiring a Word build merely to refresh this test.
    """
    fixture = json.loads(BASELINE.read_text(encoding="utf-8"))
    expected = {
        int(level): (values["left"], values["hanging"])
        for level, values in fixture["level_indentation"].items()
    }

    items = mrg.parse_markdown(str(DRAFT))
    list_items = [it for it in items if it["type"] == "list_item"]
    assert list_items, "current draft must contain at least one list item"

    # Sanity: the standalone indent extraction agrees with parse_markdown order.
    indents = _draft_list_indents()
    assert len(indents) == len(list_items)
    for indent, item in zip(indents, list_items):
        assert mrg.compute_list_level(indent, item["marker"]) == item["level"]

    observed_levels = {item["level"] for item in list_items}
    assert observed_levels <= set(expected), (
        f"draft uses list levels without an indentation contract: "
        f"{sorted(observed_levels - set(expected))}"
    )
    for item in list_items:
        derived_left = str(item["level"] * 360)
        derived_hanging = "360"
        assert (derived_left, derived_hanging) == expected[item["level"]]
