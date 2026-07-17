"""Property test for the Assembler's "exactly once on success" guarantee (R7.5)
of the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 18: Perakitan sukses memunculkan setiap entri tepat
satu kali** — for every assembly that completes without error, each
Kerangka_Bab entry appears exactly once in the resulting Berkas_Draf.

``assemble`` is a pure transform (design.md §9 "Assembler"), so 100+ Hypothesis
iterations are cheap.
"""
import sys
from collections import Counter
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (pure core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.assembler import assemble  # noqa: E402
from alur_penulisan.models import (  # noqa: E402
    ContentBlock,
    Level,
    Paragraph,
    Skeleton,
    SkeletonEntry,
)

# --------------------------------------------------------------------------- #
# Generators
# --------------------------------------------------------------------------- #
_TITLE_ALPHABET = "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LEVELS = [Level.BAB, Level.SUBBAB, Level.SUBSUBBAB]


@st.composite
def _valid_skeleton_and_contents(draw):
    """Build a valid ``(Skeleton, contents)`` pair.

    * Entry ids are unique (``e0``, ``e1``, ...).
    * ``numbering`` is unique per entry (its index), guaranteeing every entry
      produces a distinct heading text so occurrence counting is unambiguous.
    * Every entry has a matching content block (assembly succeeds — no missing
      entry, no orphan content).
    """
    count = draw(st.integers(min_value=1, max_value=8))

    entries: list[SkeletonEntry] = []
    contents: dict[str, ContentBlock] = {}

    for i in range(count):
        entry_id = f"e{i}"
        # Unique numbering per entry -> unique heading text even if titles clash.
        numbering = f"{i + 1}."
        title = draw(st.text(alphabet=_TITLE_ALPHABET, min_size=1, max_size=12)).strip()
        if not title:
            title = f"Judul {i}"
        level = draw(st.sampled_from(_LEVELS))
        owner_role = draw(st.sampled_from(["iman", "dwikhi", "faiz"]))

        entries.append(
            SkeletonEntry(
                entry_id=entry_id,
                numbering=numbering,
                title=title,
                level=level,
                owner_role=owner_role,
            )
        )

        # Complete content for the entry (0..3 paragraphs).
        n_paras = draw(st.integers(min_value=0, max_value=3))
        paragraphs = [
            Paragraph(text=draw(st.text(alphabet=_TITLE_ALPHABET, min_size=1, max_size=20)).strip() or f"isi {i}.{p}")
            for p in range(n_paras)
        ]
        contents[entry_id] = ContentBlock(entry_id=entry_id, paragraphs=paragraphs)

    return Skeleton(entries=tuple(entries)), contents


def _expected_heading_text(entry: SkeletonEntry) -> str:
    """Mirror the assembler's heading-text construction for an entry."""
    title = entry.title.strip()
    numbering = entry.numbering.strip()
    if numbering and not title.startswith(numbering):
        return f"{numbering} {title}"
    return title


# =========================================================================== #
# Property 18: Perakitan sukses memunculkan setiap entri tepat satu kali
# =========================================================================== #
# Feature: automated-writing-workflow, Property 18: Perakitan sukses memunculkan setiap entri tepat satu kali
# Validates: Requirements 7.5
@settings(max_examples=200, deadline=None)
@given(data=_valid_skeleton_and_contents())
def test_successful_assembly_emits_each_entry_exactly_once(data):
    skeleton, contents = data

    draft, findings = assemble(skeleton, contents)

    # A successful assembly reports no fatal findings.
    assert findings == []

    # Every skeleton entry must surface as exactly one heading in the draft.
    heading_texts = Counter(
        str(h.meta.get("text", "")).strip() for h in draft.headings()
    )

    # Total headings equal the number of entries (no extra/missing headings).
    assert sum(heading_texts.values()) == len(skeleton.entries), (
        f"expected {len(skeleton.entries)} headings, got {sum(heading_texts.values())}"
    )

    for entry in skeleton.entries:
        expected = _expected_heading_text(entry)
        assert heading_texts[expected] == 1, (
            f"entry {entry.entry_id!r} heading {expected!r} appears "
            f"{heading_texts[expected]} times, expected exactly 1"
        )
