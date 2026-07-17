"""Property test for the Assembler's missing-content stop rule (R7.3) of the
automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 19: Entri tanpa konten menghentikan perakitan tanpa
draf sebagian** — for any Kerangka_Bab with one or more entries whose content
is missing, ``assemble`` stops and raises :class:`AssemblyError` naming every
entry whose content is missing, without producing a partial Berkas_Draf.

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
    BlockKind,
    ContentBlock,
    Level,
    Paragraph,
    Skeleton,
    SkeletonEntry,
)


@st.composite
def _skeleton_with_missing_contents(draw):
    """Build a Skeleton plus a contents mapping that omits >=1 entry's content.

    Entry ids are unique so the missing set is unambiguous. A non-empty random
    subset of entries is dropped from the contents mapping; every remaining
    entry gets a valid ContentBlock. Returns ``(skeleton, contents,
    missing_ids)`` where ``missing_ids`` is the exact set of entry ids whose
    content is absent.
    """
    n = draw(st.integers(min_value=1, max_value=8))
    entry_ids = [f"entry-{i}" for i in range(n)]

    entries = []
    for i, entry_id in enumerate(entry_ids):
        level = draw(st.sampled_from(list(Level)))
        entries.append(
            SkeletonEntry(
                entry_id=entry_id,
                numbering=str(i + 1),
                title=draw(st.text(min_size=1, max_size=20)).strip() or f"Judul {i}",
                level=level,
                owner_role=draw(st.sampled_from(["iman", "dwikhi", "faiz"])),
            )
        )
    skeleton = Skeleton(entries=tuple(entries))

    # Choose a non-empty subset of entry ids whose content will be missing.
    missing_ids = set(
        draw(
            st.lists(
                st.sampled_from(entry_ids),
                min_size=1,
                unique=True,
            )
        )
    )

    contents: dict[str, ContentBlock] = {}
    for entry_id in entry_ids:
        if entry_id in missing_ids:
            continue
        contents[entry_id] = ContentBlock(
            entry_id=entry_id,
            paragraphs=[Paragraph(text=draw(st.text(min_size=0, max_size=30)))],
            kind=BlockKind.GENERATED,
        )

    return skeleton, contents, missing_ids


# =========================================================================== #
# Property 19: Entri tanpa konten menghentikan perakitan tanpa draf sebagian
# =========================================================================== #
# Feature: automated-writing-workflow, Property 19: Entri tanpa konten menghentikan perakitan tanpa draf sebagian
# Validates: Requirements 7.3
@settings(max_examples=100, deadline=None)
@given(data=_skeleton_with_missing_contents())
def test_missing_content_stops_assembly_without_partial_draft(data):
    skeleton, contents, missing_ids = data

    with pytest.raises(AssemblyError) as excinfo:
        # No draft is returned: assemble raises before building any DraftModel,
        # so there is no partial Berkas_Draf output.
        assemble(skeleton, contents)

    error = excinfo.value

    # The error names every entry whose content is missing (exact set).
    assert set(error.missing_entries) == missing_ids, (
        f"missing_entries={error.missing_entries!r} should name exactly the "
        f"entries without content {sorted(missing_ids)!r}"
    )

    # Each missing entry id is surfaced in the human-readable message too.
    message = str(error)
    for entry_id in missing_ids:
        assert entry_id in message, (
            f"missing entry {entry_id!r} not named in error message: {message!r}"
        )
