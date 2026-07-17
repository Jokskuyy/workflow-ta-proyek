"""Property test for the Assembler's order & depth guarantee (R7.1) of the
automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 17: Perakitan mempertahankan urutan dan kedalaman
Kerangka_Bab** — for any valid Skeleton paired with complete content, the
assembled draft lays out its chapter/sub-chapter headings in exactly the same
order and at exactly the same depth (heading level) as the entries of the
Kerangka_Bab.

``assemble`` is a pure transform, so 100+ Hypothesis iterations are cheap.
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

from alur_penulisan.assembler import _heading_line, assemble  # noqa: E402
from alur_penulisan.models import (  # noqa: E402
    BlockKind,
    ContentBlock,
    Level,
    Paragraph,
    Skeleton,
    SkeletonEntry,
)

# Text used for titles / numbering / paragraphs. Kept off control characters so
# the generated Markdown headings stay well-formed and comparable.
_TEXT = st.text(
    alphabet=st.characters(
        min_codepoint=32, max_codepoint=0x2FFF, blacklist_categories=("Cc", "Cs")
    ),
    min_size=0,
    max_size=24,
)


@st.composite
def _skeleton_and_contents(draw):
    """Build a random *valid* Skeleton plus a *complete* contents mapping.

    Validity requirements exercised here:

    * ``entry_id`` values are unique (they key the ``contents`` mapping and the
      draft layout is one heading per entry).
    * levels are drawn freely from ``BAB``/``SUBBAB``/``SUBSUBBAB`` so order and
      depth vary independently.
    * every entry has an associated :class:`ContentBlock` (no missing content,
      no orphan content), so ``assemble`` succeeds and emits every entry.
    """
    n = draw(st.integers(min_value=0, max_value=8))
    entry_ids = draw(
        st.lists(
            st.text(
                alphabet=st.characters(min_codepoint=48, max_codepoint=122),
                min_size=1,
                max_size=8,
            ),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )

    entries = []
    contents = {}
    for entry_id in entry_ids:
        level = draw(st.sampled_from(list(Level)))
        entries.append(
            SkeletonEntry(
                entry_id=entry_id,
                numbering=draw(_TEXT),
                title=draw(_TEXT),
                level=level,
                owner_role=draw(st.sampled_from(["iman", "dwikhi", "faiz"])),
            )
        )
        paragraphs = draw(
            st.lists(
                _TEXT.map(lambda t: Paragraph(text=t)),
                min_size=1,
                max_size=3,
            )
        )
        contents[entry_id] = ContentBlock(
            entry_id=entry_id,
            paragraphs=paragraphs,
            kind=BlockKind.GENERATED,
        )

    return Skeleton(entries=tuple(entries)), contents


# =========================================================================== #
# Property 17: Perakitan mempertahankan urutan dan kedalaman Kerangka_Bab
# =========================================================================== #
# Feature: automated-writing-workflow, Property 17: Perakitan mempertahankan urutan dan kedalaman Kerangka_Bab
# Validates: Requirements 7.1
@settings(max_examples=200, deadline=None)
@given(data=_skeleton_and_contents())
def test_assembly_preserves_order_and_depth(data):
    skeleton, contents = data

    draft, findings = assemble(skeleton, contents)

    headings = draft.headings()

    # One heading per skeleton entry, no more, no fewer.
    assert len(headings) == len(skeleton.entries), (
        f"expected {len(skeleton.entries)} headings, got {len(headings)}"
    )

    # Depth sequence: heading level i matches entry level i exactly.
    assembled_levels = [h.meta["level"] for h in headings]
    expected_levels = [e.level.value for e in skeleton.entries]
    assert assembled_levels == expected_levels, (
        f"depth mismatch: assembled={assembled_levels}, expected={expected_levels}"
    )

    # Order sequence: heading line i matches the canonical rendering of entry i,
    # in the same position — same order as the Kerangka_Bab entries.
    for i, entry in enumerate(skeleton.entries):
        assert headings[i].lines[0] == _heading_line(entry), (
            f"heading {i} mismatch: {headings[i].lines[0]!r} != "
            f"{_heading_line(entry)!r}"
        )
