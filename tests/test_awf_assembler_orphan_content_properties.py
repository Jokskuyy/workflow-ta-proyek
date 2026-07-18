"""Property test for the Assembler's orphan-content guard (R7.4) of the
automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 20: Konten yatim menghentikan perakitan tanpa draf
sebagian** — for any content mapping that carries one or more keys with no
matching Kerangka_Bab entry (orphans), while every skeleton entry still has its
own content, ``assemble`` stops and raises :class:`AssemblyError` naming every
orphan content key, without producing a partial draft.

``assemble`` is a pure transform, so 100+ Hypothesis iterations are cheap.
"""
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (pure core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.assembler import assemble  # noqa: E402
from alur_penulisan.exceptions import AssemblyError  # noqa: E402
from alur_penulisan.models import (  # noqa: E402
    ContentBlock,
    Level,
    Paragraph,
    Skeleton,
    SkeletonEntry,
)

# Distinct token spaces so skeleton entry ids and orphan keys never collide.
_ENTRY_IDS = st.text(alphabet="abcdefghijklmnop", min_size=1, max_size=6)
_ORPHAN_IDS = st.text(alphabet="ORPHAN0123456789_", min_size=1, max_size=8)
_LEVELS = st.sampled_from(list(Level))


def _make_entry(entry_id: str) -> SkeletonEntry:
    return SkeletonEntry(
        entry_id=entry_id,
        numbering=entry_id,
        title=f"Judul {entry_id}",
        level=Level.BAB,
        owner_role="iman",
    )


def _make_content(entry_id: str) -> ContentBlock:
    return ContentBlock(
        entry_id=entry_id,
        paragraphs=[Paragraph(text=f"Isi untuk {entry_id}.")],
    )


@st.composite
def _skeleton_with_orphans(draw):
    """Build a (skeleton, contents) pair where every skeleton entry has content
    but ``contents`` additionally carries >=1 orphan key with no skeleton entry.
    """
    entry_ids = draw(
        st.lists(_ENTRY_IDS, min_size=0, max_size=6, unique=True)
    )
    # Orphan keys must be disjoint from the (letter-only) entry ids; the
    # dedicated alphabet already guarantees no overlap, but filter defensively.
    entry_id_set = set(entry_ids)
    orphan_ids = draw(
        st.lists(_ORPHAN_IDS, min_size=1, max_size=5, unique=True).filter(
            lambda ks: all(k not in entry_id_set for k in ks)
        )
    )

    entries = tuple(_make_entry(eid) for eid in entry_ids)
    skeleton = Skeleton(entries=entries)

    # Every skeleton entry DOES have content, so only the orphan condition fires.
    contents = {eid: _make_content(eid) for eid in entry_ids}
    for oid in orphan_ids:
        contents[oid] = _make_content(oid)

    return skeleton, contents, set(orphan_ids)


# =========================================================================== #
# Property 20: Konten yatim menghentikan perakitan tanpa draf sebagian
# =========================================================================== #
# Feature: automated-writing-workflow, Property 20: Konten yatim menghentikan perakitan tanpa draf sebagian
# Validates: Requirements 7.4
@settings(max_examples=100, deadline=None)
@given(data=_skeleton_with_orphans())
def test_orphan_content_halts_assembly_without_partial_draft(data):
    skeleton, contents, orphan_ids = data

    with pytest.raises(AssemblyError) as excinfo:
        assemble(skeleton, contents)

    err = excinfo.value

    # No partial Berkas_Draf leaks: the error carries no draft; assemble returned
    # nothing (the raise happened before any DraftModel was constructed).
    # Every orphan content key is named in the error's orphan_contents.
    reported = set(err.orphan_contents)
    assert reported == orphan_ids, (
        f"orphan_contents {sorted(reported)} did not match expected "
        f"{sorted(orphan_ids)}"
    )

    # No skeleton entry is missing content, so missing_entries stays empty:
    # only the orphan condition triggered the halt.
    assert err.missing_entries == ()

    # The human-facing message names every orphan content key.
    message = str(err)
    for oid in orphan_ids:
        assert oid in message, (
            f"orphan key {oid!r} not mentioned in AssemblyError message: {message!r}"
        )
