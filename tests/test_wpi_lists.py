"""Property + unit tests for list nesting by indentation (R3) of the
writing-pipeline-improvements spec.

Spec: .kiro/specs/writing-pipeline-improvements

Covers:
  * design Property 9 (compute_list_level depends only on indentation, indent 0
    -> outermost level, monotonic non-decreasing, marker is cosmetic).
  * backward-compatibility (R3.4): the current Draf, parsed with the new
    indentation-based level computation, reproduces the captured baseline list
    levels in tests/fixtures/wpi_baseline_list_levels.json.

``compute_list_level`` is a pure, deterministic transform so 100+ Hypothesis
iterations are cheap.
"""
import json
import re
import sys
from collections import defaultdict
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
# Backward-compatibility (R3.4 / R3.5): current Draf reproduces the baseline.
# --------------------------------------------------------------------------- #
_LIST_RE = re.compile(r'^(\s*)([0-9a-zA-Z]+[.\)])\s+(.*)$')


def _draft_list_indents():
    """Leading-indent width of every list item in the current Draf, in order.

    Mirrors the gating of ``parse_markdown`` (only content from '# BAB I'
    onward, skipping code blocks and [TABLE] blocks) so the sequence lines up
    1:1 with the parsed list_items and the captured baseline.
    """
    lines = DRAFT.read_text(encoding="utf-8").splitlines(keepends=True)
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
    """Each current-Draf list paragraph's derived ind left/hanging equals the
    captured baseline in wpi_baseline_list_levels.json.

    The baseline records the FINAL rendered indentation per list paragraph
    (left/hanging dxa). Backward compatibility means the new
    indentation-based ``compute_list_level`` must place every list item in the
    same indentation "bucket" as the baseline, i.e. items sharing a baseline
    (left, hanging) must share a computed level and vice versa.
    """
    fixture = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline = fixture["list_levels"]

    # The parsed list_items must line up 1:1 with the captured baseline.
    items = mrg.parse_markdown(str(DRAFT))
    list_items = [it for it in items if it["type"] == "list_item"]
    assert len(list_items) == len(baseline) == fixture["count"], (
        f"list item count mismatch: parsed={len(list_items)} "
        f"baseline={len(baseline)} count={fixture['count']}"
    )

    # Sanity: the standalone indent extraction agrees with parse_markdown order.
    indents = _draft_list_indents()
    assert len(indents) == len(list_items)
    for indent, item in zip(indents, list_items):
        assert mrg.compute_list_level(indent, item["marker"]) == item["level"]

    # The computed level must partition the items consistently with the
    # baseline (left, hanging): one distinct ind per level, and vice versa.
    level_to_ind = defaultdict(set)
    ind_to_level = defaultdict(set)
    for item, base in zip(list_items, baseline):
        ind = (base["left"], base["hanging"])
        level_to_ind[item["level"]].add(ind)
        ind_to_level[ind].add(item["level"])

    for level, inds in level_to_ind.items():
        assert len(inds) == 1, f"level {level} maps to multiple baseline ind values: {inds}"
    for ind, levels in ind_to_level.items():
        assert len(levels) == 1, f"baseline ind {ind} maps to multiple levels: {levels}"

    # Lock the concrete baseline mapping observed for the current Draf
    # (level 1 -> 360/360, level 2 -> None/360, level 3 -> 1080/360).
    expected = {
        1: ("360", "360"),
        2: (None, "360"),
        3: ("1080", "360"),
    }
    observed = {lvl: next(iter(inds)) for lvl, inds in level_to_ind.items()}
    assert observed == expected, f"baseline ind mapping changed: {observed}"

    # Direct positional assertion: derived ind == baseline ind for every item.
    for item, base in zip(list_items, baseline):
        derived_left, derived_hanging = expected[item["level"]]
        assert derived_left == base["left"]
        assert derived_hanging == base["hanging"]
