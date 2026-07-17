"""Property-based tests for the SkeletonGenerator of the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers task 3.2 (Property 1) against the PURE SkeletonGenerator helpers exposed by
``skills/scripts/alur_penulisan/skeleton.py``:

  generate_skeleton, canonical_skeleton, title_matches, entry_heading_text.

Skeleton generation is a pure text-in/text-out transformation, so 100+ Hypothesis
iterations are cheap. The existing pipeline test suites are NOT modified; this is a
brand-new file. Nothing here touches disk — the DraftModel is built in memory.
"""
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the SkeletonGenerator from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.skeleton import (  # noqa: E402
    canonical_skeleton,
    entry_heading_text,
    generate_skeleton,
    title_matches,
)
from alur_penulisan.draft_model import DraftModel  # noqa: E402

# The canonical Kerangka_Bab is fixed data (BAB I-IV + baseline sub-chapters).
_CANONICAL = canonical_skeleton()
_ENTRIES = _CANONICAL.entries


# --------------------------------------------------------------------------- #
# Strategies: build arbitrary INITIAL draft states (empty or partial).
# --------------------------------------------------------------------------- #
def _vary_case_and_edge_ws(draw: st.DrawFn, text: str) -> str:
    """Return ``text`` with random letter-case flips and random edge whitespace.

    Only case and leading/trailing spaces are altered (internal spacing is kept
    intact) so the result still matches the canonical title under
    :func:`title_matches` (Requirement 1.3 comparison rule).
    """
    flips = draw(st.lists(st.booleans(), min_size=len(text), max_size=len(text)))
    varied = "".join(c.upper() if f else c.lower() for c, f in zip(text, flips))
    lead = " " * draw(st.integers(min_value=0, max_value=3))
    trail = " " * draw(st.integers(min_value=0, max_value=3))
    return f"{lead}{varied}{trail}"


# Simple manual body text that never opens another block type (no '#', '---',
# list markers, tables, fences) so it cannot be mistaken for a heading.
_MANUAL_PARAGRAPH = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs"), min_codepoint=32),
    min_size=1,
    max_size=40,
).map(lambda s: s.replace("#", "").replace("|", "").replace("`", "").strip() or "isi manual")


@st.composite
def partial_drafts(draw: st.DrawFn) -> DraftModel:
    """Generate an initial :class:`DraftModel`: empty or partially populated.

    A random subset of canonical entries is pre-seeded as headings (rendered at
    the correct Markdown depth for their level, with case/edge-whitespace noise
    on the title text), optionally interleaved with manual paragraphs and an
    optional preamble, and optionally shuffled out of canonical order.
    """
    n = len(_ENTRIES)
    include = draw(st.lists(st.booleans(), min_size=n, max_size=n))
    selected = [entry for entry, inc in zip(_ENTRIES, include) if inc]

    # Optionally present the existing headings out of canonical order.
    if draw(st.booleans()):
        selected = draw(st.permutations(selected))

    lines: list[str] = []
    # Optional front matter / preamble.
    if draw(st.booleans()):
        lines.append(draw(_MANUAL_PARAGRAPH))
        lines.append("")

    for entry in selected:
        prefix = "#" * entry.level.value
        title = _vary_case_and_edge_ws(draw, entry_heading_text(entry))
        lines.append(f"{prefix} {title}")
        lines.append("")
        if draw(st.booleans()):
            lines.append(draw(_MANUAL_PARAGRAPH))
            lines.append("")

    return DraftModel.from_markdown("\n".join(lines))


# --------------------------------------------------------------------------- #
# Property 1
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 1: Kelengkapan dan urutan Kerangka_Bab
@settings(max_examples=100)
@given(draft=partial_drafts())
def test_property_1_skeleton_completeness_and_order(draft: DraftModel) -> None:
    """Property 1: Kelengkapan dan urutan Kerangka_Bab.

    Untuk setiap keadaan awal Berkas_Draf (kosong maupun sebagian), hasil
    pembuatan Kerangka_Bab memuat seluruh entri baku BAB I sampai BAB IV beserta
    sub-bab bakunya dari outline kanonik, dalam urutan kanonik yang sama, dengan
    penomoran hierarkis yang sesuai dengan level tiap entri.

    Validates: Requirements 1.1, 1.2
    """
    result, _findings = generate_skeleton(draft)
    result_headings = result.headings()

    positions: list[int] = []
    for entry in _ENTRIES:
        target = entry_heading_text(entry)
        matches = [
            idx
            for idx, block in enumerate(result_headings)
            if title_matches(block.meta.get("text", ""), target)
        ]

        # Completeness: every canonical entry is present exactly once. Because
        # title_matches compares against the canonical heading text (which carries
        # the hierarchical numbering), an exact match also proves the displayed
        # numbering is correct (Requirement 1.1).
        assert len(matches) == 1, (
            f"entri kanonik {target!r} muncul {len(matches)} kali, harus tepat 1"
        )

        # Hierarchical numbering: the Markdown heading depth reflects the entry
        # level (BAB -> '#', SUBBAB -> '##', SUBSUBBAB -> '###') (Requirement 1.2).
        matched_block = result_headings[matches[0]]
        assert matched_block.meta.get("level") == entry.level.value, (
            f"level heading {target!r} = {matched_block.meta.get('level')}, "
            f"harus {entry.level.value}"
        )

        positions.append(matches[0])

    # Order: the canonical entries appear in the result in canonical reading order.
    assert positions == sorted(positions), (
        "entri kanonik tidak muncul dalam urutan kanonik yang sama"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
