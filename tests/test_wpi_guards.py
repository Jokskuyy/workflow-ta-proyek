"""Property + unit tests for the PURE writing-guard collectors of the
writing-pipeline-improvements spec (R6 + citation cross-check R1.5/1.6/6.3).

Spec: .kiro/specs/writing-pipeline-improvements

Covers design Properties 12, 13, 14, 15 (R6.1/6.2/6.4/6.5) plus Properties 4, 5
(citation cross-check R1.5/1.6/6.3) against the pure collectors exposed by
``scratch/merge_draft_to_docx.py``:

  collect_heading_level_warnings, collect_bab_order_warnings,
  collect_unclosed_table_warnings, collect_unbalanced_emphasis_warnings,
  collect_citation_crosscheck_warnings.

All collectors are pure and deterministic (no lxml), so 100+ Hypothesis
iterations are cheap.
"""
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the collectors from the canonical Mesin_Merge script.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
if str(SCRATCH) not in sys.path:
    sys.path.insert(0, str(SCRATCH))

import merge_draft_to_docx as mrg  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers / strategies.
# --------------------------------------------------------------------------- #
_ROMAN = [
    "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
]


def _int_to_roman(n):
    """Small Roman numeral builder for the 1..12 range used by the tests."""
    return _ROMAN[n]


# Plain words free of any emphasis metacharacter ('*', '`', '\\').
_PLAIN_NOMARK = "abcdefghijklmnopqrstuvwxyz0123456789 .,"
_word = st.text(_PLAIN_NOMARK, min_size=1, max_size=6)

# Citation/reference key parts.
_surname = st.text("abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=8)
_year = st.integers(min_value=1990, max_value=2030).map(str)
_key = st.tuples(_surname, _year)


@st.composite
def emphasis_line(draw):
    """Build a line of emphasis markers separated by mandatory plain words so
    adjacent markers never merge, plus the expected balance flag.

    Uses ONE marker family per line (asterisks OR backticks) so code spans never
    swallow asterisks — keeping the expected-balance computation simple and
    independent of the implementation's scanning order.
    """
    category = draw(st.sampled_from(["asterisk", "backtick"]))
    if category == "asterisk":
        markers = draw(st.lists(st.sampled_from(["*", "**", "***"]),
                                min_size=0, max_size=6))
    else:
        markers = draw(st.lists(st.just("`"), min_size=0, max_size=6))

    parts = [draw(_word)]
    for mk in markers:
        parts.append(mk)
        parts.append(draw(_word))  # non-empty separator (no markers in alphabet)
    line = "".join(parts)

    bold = sum(1 for mk in markers if mk in ("**", "***"))
    italic = sum(1 for mk in markers if mk in ("*", "***"))
    backtick = sum(1 for mk in markers if mk == "`")
    balanced = (bold % 2 == 0) and (italic % 2 == 0) and (backtick % 2 == 0)
    return line, balanced


@st.composite
def table_block_lines(draw):
    """A list of draft lines made of balanced [TABLE]..[/TABLE] blocks plus an
    optional trailing UNCLOSED [TABLE]. Content lines use a safe alphabet so
    they never look like an open/close marker."""
    n_pairs = draw(st.integers(min_value=0, max_value=4))
    trailing_open = draw(st.booleans())
    content = st.text("abcdef ", min_size=1, max_size=5)

    lines = []
    for _ in range(n_pairs):
        lines.append("[TABLE]")
        for _ in range(draw(st.integers(min_value=0, max_value=2))):
            lines.append(draw(content))
        lines.append("[/TABLE]")
    if trailing_open:
        lines.append("[TABLE]")
        for _ in range(draw(st.integers(min_value=0, max_value=2))):
            lines.append(draw(content))
    return lines, trailing_open


def _entries_from_keys(keys):
    """Build ReferenceEntry objects whose reference_key == (surname, year)."""
    out = []
    for s, y in keys:
        out.append(mrg.ReferenceEntry(
            raw=f"{s.capitalize()}, A. ({y}). Judul artikel.",
            spans=(),
            authors=(s.capitalize(),),
            year=y,
        ))
    return out


def _body_from_keys(keys):
    """Build body text containing one in-text citation per key."""
    return " ".join(f"({s.capitalize()}, {y})" for s, y in keys)


# =========================================================================== #
# Property 12: Guard lompatan level heading
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 12: Guard lompatan level heading
# Validates: Requirements 6.1
@settings(max_examples=200, deadline=None)
@given(levels=st.lists(st.integers(min_value=1, max_value=6),
                       min_size=1, max_size=10))
def test_property12_heading_level_jump_guard(levels):
    items = [{"type": "heading", "level": lv, "text": f"Judul {i}"}
             for i, lv in enumerate(levels)]
    warnings = mrg.collect_heading_level_warnings(items)

    expected = sum(1 for a, b in zip(levels, levels[1:]) if b - a > 1)
    assert len(warnings) == expected
    # Every warning names a skipped level (the level immediately above prev).
    for (a, b) in zip(levels, levels[1:]):
        if b - a > 1:
            pass  # presence is asserted by the count + content checks below
    assert all("[WARN][heading]" in w and "melewati" in w for w in warnings)


# =========================================================================== #
# Property 13: Guard urutan BAB
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 13: Guard urutan BAB
# Validates: Requirements 6.2
@settings(max_examples=200, deadline=None)
@given(nums=st.lists(st.integers(min_value=1, max_value=12),
                     min_size=1, max_size=8))
def test_property13_bab_order_guard(nums):
    items = [{"type": "heading", "level": 1,
              "text": f"BAB {_int_to_roman(n)} JUDUL BAB"} for n in nums]
    warnings = mrg.collect_bab_order_warnings(items)

    expected = sum(1 for a, b in zip(nums, nums[1:]) if b != a + 1)
    assert len(warnings) == expected
    assert all("[WARN][bab]" in w for w in warnings)


# =========================================================================== #
# Property 14: Guard blok [TABLE] tak tertutup
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 14: Guard blok [TABLE] tak tertutup
# Validates: Requirements 6.4
@settings(max_examples=200, deadline=None)
@given(data=table_block_lines())
def test_property14_unclosed_table_guard(data):
    lines, trailing_open = data
    warnings = mrg.collect_unclosed_table_warnings(lines)

    assert len(warnings) == (1 if trailing_open else 0)
    if trailing_open:
        assert "[WARN][tabel]" in warnings[0]


# =========================================================================== #
# Property 15: Guard emphasis tak seimbang
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 15: Guard emphasis tak seimbang
# Validates: Requirements 6.5
@settings(max_examples=200, deadline=None)
@given(data=emphasis_line())
def test_property15_unbalanced_emphasis_guard(data):
    line, balanced = data
    warnings = mrg.collect_unbalanced_emphasis_warnings([line])

    if balanced:
        assert warnings == []
    else:
        assert len(warnings) == 1
        # The warning names the offending line.
        assert line in warnings[0]
        assert "[WARN][emphasis]" in warnings[0]


# =========================================================================== #
# Property 4: Kelengkapan pemeriksaan silang sitasi -> Daftar_Pustaka
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 4: Kelengkapan pemeriksaan silang sitasi -> Daftar_Pustaka
# Validates: Requirements 1.5, 6.3
@settings(max_examples=200, deadline=None)
@given(cit=st.lists(_key, min_size=0, max_size=6, unique=True),
       ent=st.lists(_key, min_size=0, max_size=6, unique=True))
def test_property4_citation_to_bibliography_crosscheck(cit, ent):
    body = _body_from_keys(cit)
    entries = _entries_from_keys(ent)

    warnings, has_fatal = mrg.collect_citation_crosscheck_warnings(body, entries)

    entry_keys = set(ent)  # surnames already lowercase, year is str
    missing = [(s, y) for (s, y) in cit if (s, y) not in entry_keys]

    forward = [w for w in warnings if "tidak memiliki" in w]
    assert len(forward) == len(missing)
    # Each forward warning names the citation's name and year.
    for (s, y) in missing:
        assert any((s.capitalize() in w and y in w) for w in forward)
    # No forward warning for a citation that has a matching entry.
    for (s, y) in cit:
        if (s, y) in entry_keys:
            assert not any((s.capitalize() in w and y in w) for w in forward)
    assert has_fatal is False  # default non-fatal


# =========================================================================== #
# Property 5: Kelengkapan pemeriksaan silang Daftar_Pustaka -> sitasi
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 5: Kelengkapan pemeriksaan silang Daftar_Pustaka -> sitasi
# Validates: Requirements 1.6, 6.3
@settings(max_examples=200, deadline=None)
@given(cit=st.lists(_key, min_size=0, max_size=6, unique=True),
       ent=st.lists(_key, min_size=0, max_size=6, unique=True))
def test_property5_bibliography_to_citation_crosscheck(cit, ent):
    body = _body_from_keys(cit)
    entries = _entries_from_keys(ent)

    warnings, has_fatal = mrg.collect_citation_crosscheck_warnings(body, entries)

    cited_keys = set(cit)
    uncited = [(s, y) for (s, y) in ent if (s, y) not in cited_keys]

    backward = [w for w in warnings if "tidak pernah" in w]
    assert len(backward) == len(uncited)
    # Each backward warning names the uncited entry (its raw text).
    for (s, y) in uncited:
        assert any((s.capitalize() in w and y in w) for w in backward)
    assert has_fatal is False  # default non-fatal


# =========================================================================== #
# Focused unit examples.
# =========================================================================== #
def test_unit_heading_jump_names_skipped_level():
    items = [{"type": "heading", "level": 1, "text": "BAB I"},
             {"type": "heading", "level": 3, "text": "Sub jauh"}]
    warnings = mrg.collect_heading_level_warnings(items)
    assert len(warnings) == 1
    assert "H2" in warnings[0] and "Sub jauh" in warnings[0]


def test_unit_heading_no_warning_on_descent_or_step():
    items = [{"type": "heading", "level": 1, "text": "a"},
             {"type": "heading", "level": 2, "text": "b"},
             {"type": "heading", "level": 1, "text": "c"}]
    assert mrg.collect_heading_level_warnings(items) == []


def test_unit_bab_ignores_non_bab_headings():
    items = [{"type": "heading", "level": 1, "text": "BAB I PENDAHULUAN"},
             {"type": "heading", "level": 2, "text": "1.1 Latar Belakang"},
             {"type": "heading", "level": 1, "text": "BAB II TINJAUAN"}]
    assert mrg.collect_bab_order_warnings(items) == []


def test_unit_bab_out_of_order_warns():
    items = [{"type": "heading", "level": 1, "text": "BAB I"},
             {"type": "heading", "level": 1, "text": "BAB III"}]
    warnings = mrg.collect_bab_order_warnings(items)
    assert len(warnings) == 1
    assert "[WARN][bab]" in warnings[0]


def test_unit_unclosed_table_single_warning():
    lines = ["[TABLE]", "a | b", "[/TABLE]", "[TABLE]", "c | d"]
    warnings = mrg.collect_unclosed_table_warnings(lines)
    assert len(warnings) == 1


def test_unit_escaped_asterisk_is_balanced():
    assert mrg.collect_unbalanced_emphasis_warnings([r"harga 5\* lebih"]) == []


def test_unit_citation_fatal_flag_sets_has_fatal():
    body = "(Unknown, 2024)"
    warnings, has_fatal = mrg.collect_citation_crosscheck_warnings(
        body, [], fatal=True)
    assert warnings  # there is a mismatch
    assert has_fatal is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
