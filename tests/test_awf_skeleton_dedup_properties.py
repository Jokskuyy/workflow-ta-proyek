"""Property test for the SkeletonGenerator's duplicate-title prevention (R1.3) of
the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 2: Tidak ada duplikasi judul kerangka** — for any
Berkas_Draf that already contains some canonical baseline titles in case /
edge-whitespace variations, after ``generate_skeleton`` every canonical entry
appears exactly once (a matching existing title is preserved, not duplicated).

``generate_skeleton`` is a pure transform, so 100+ Hypothesis iterations are
cheap.
"""
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (pure core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.skeleton import (  # noqa: E402
    canonical_skeleton,
    entry_heading_text,
    generate_skeleton,
    title_matches,
)

_ENTRIES = canonical_skeleton().entries


@st.composite
def _vary_case(draw, text: str) -> str:
    """Return ``text`` with each cased character randomly upper/lower/unchanged.

    Internal spacing is preserved (significant); only letter case is perturbed,
    which is exactly the variation R1.3 must ignore.
    """
    out = []
    for ch in text:
        out.append(draw(st.sampled_from([ch, ch.upper(), ch.lower()])))
    return "".join(out)


@st.composite
def _partial_draft(draw):
    """Build a draft pre-populated with a random subset of canonical headings.

    Each pre-existing heading uses a case-varied form plus random leading/
    trailing whitespace (edge whitespace R1.3 must also ignore). Returns the
    Markdown text together with the mapping ``entry_id -> normalized varied
    heading text`` for the entries that were pre-included, so the test can also
    assert those titles are *preserved* (not regenerated to canonical case).
    """
    indices = sorted(
        draw(
            st.lists(
                st.integers(min_value=0, max_value=len(_ENTRIES) - 1),
                unique=True,
            )
        )
    )
    included = set(indices)

    lines: list[str] = []
    preserved: dict[str, str] = {}
    for idx, entry in enumerate(_ENTRIES):
        if idx not in included:
            continue
        base = entry_heading_text(entry)
        varied = draw(_vary_case(base))
        lead = " " * draw(st.integers(min_value=0, max_value=2))
        trail = " " * draw(st.integers(min_value=0, max_value=2))
        prefix = "#" * entry.level.value
        lines.append(f"{prefix} {lead}{varied}{trail}")
        lines.append("")
        # Occasionally add a manual content paragraph under the heading.
        if draw(st.booleans()):
            lines.append("Konten manual yang harus dipertahankan.")
            lines.append("")
        # The heading text as the parser will store it (edge whitespace stripped).
        preserved[entry.entry_id] = varied.strip()

    return "\n".join(lines), preserved


# =========================================================================== #
# Property 2: Tidak ada duplikasi judul kerangka
# =========================================================================== #
# Feature: automated-writing-workflow, Property 2: Tidak ada duplikasi judul kerangka
# Validates: Requirements 1.3
@settings(max_examples=100, deadline=None)
@given(data=_partial_draft())
def test_no_duplicate_skeleton_titles(data):
    text, preserved = data
    model = DraftModel.from_markdown(text)

    new_draft, findings = generate_skeleton(model)

    headings = new_draft.headings()

    # Every canonical entry appears exactly once (no duplicates introduced,
    # matching pre-existing titles preserved rather than re-added).
    for entry in _ENTRIES:
        target = entry_heading_text(entry)
        count = sum(
            1 for h in headings if title_matches(h.meta.get("text", ""), target)
        )
        assert count == 1, (
            f"entry {entry.entry_id!r} ({target!r}) appears {count} times, "
            f"expected exactly 1"
        )

    # Pre-existing (case/edge-varied) titles are preserved verbatim, i.e. the
    # generator kept the existing heading rather than regenerating it.
    heading_texts = {h.meta.get("text", "") for h in headings}
    for entry_id, kept_text in preserved.items():
        assert kept_text in heading_texts, (
            f"pre-existing heading {kept_text!r} for entry {entry_id!r} was not "
            f"preserved; headings={sorted(heading_texts)}"
        )
