"""Property test for the IdempotentMerger's Konten_Manual preservation (R8.2) of
the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 21: Konten_Manual dipertahankan utuh** — for any
Berkas_Draf that contains Konten_Manual blocks (``BlockKind.MANUAL``), after the
workflow's idempotent merge every Konten_Manual block still exists, unchanged:
not overwritten, not deleted, and its content not modified (Requirement 8.2:
"WHILE Alur_Penulisan memproses Berkas_Draf, THE Alur_Penulisan SHALL
mempertahankan seluruh Konten_Manual yang sudah ada tanpa menimpa, menghapus,
atau mengubah isinya.").

``merge`` is a pure transform, so 100+ Hypothesis iterations are cheap.
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

from alur_penulisan.draft_model import DraftBlock, DraftBlockType, DraftModel  # noqa: E402
from alur_penulisan.merger import is_manual_content, merge  # noqa: E402
from alur_penulisan.models import BlockKind  # noqa: E402

# A small pool of titles so existing and generated drafts share some headings,
# exercising both the "update in place" and "append new chapter" merge paths.
_TITLE_POOL = ["BAB I PENDAHULUAN", "Latar Belakang", "Rumusan Masalah",
               "BAB II TINJAUAN", "Metodologi", "Hasil", "Kesimpulan"]


@st.composite
def _heading_block(draw):
    """A generated heading block with a level (1-3) and a pooled title."""
    level = draw(st.integers(min_value=1, max_value=3))
    title = draw(st.sampled_from(_TITLE_POOL))
    line = f"{'#' * level} {title}"
    return DraftBlock(
        DraftBlockType.HEADING,
        [line],
        kind=BlockKind.GENERATED,
        meta={"level": level, "text": title},
    )


@st.composite
def _paragraph_block(draw, *, manual: bool):
    """A paragraph block, marked MANUAL or GENERATED per ``manual``.

    Manual blocks are given distinctive, non-empty text so a modification would
    be detectable and so the assertions remain meaningful.
    """
    words = draw(st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=1, max_size=12),
        min_size=1, max_size=3,
    ))
    prefix = "MANUAL:" if manual else "gen:"
    lines = [f"{prefix} {w.strip() or 'x'}" for w in words]
    return DraftBlock(
        DraftBlockType.PARAGRAPH,
        lines,
        kind=BlockKind.MANUAL if manual else BlockKind.GENERATED,
    )


@st.composite
def _existing_draft(draw):
    """Build an existing DraftModel with several sections, some Konten_Manual.

    Guarantees at least one MANUAL block so every generated example actually
    exercises the property.
    """
    blocks: list[DraftBlock] = []

    # Optional preamble that may itself contain a manual block.
    if draw(st.booleans()):
        blocks.append(draw(_paragraph_block(manual=draw(st.booleans()))))

    n_sections = draw(st.integers(min_value=1, max_value=4))
    for _ in range(n_sections):
        blocks.append(draw(_heading_block()))
        n_body = draw(st.integers(min_value=0, max_value=3))
        for _ in range(n_body):
            blocks.append(draw(_paragraph_block(manual=draw(st.booleans()))))

    # Ensure at least one manual block exists in the draft.
    if not any(is_manual_content(b) for b in blocks):
        blocks.append(draw(_paragraph_block(manual=True)))

    return DraftModel(blocks=blocks, trailing_newline=draw(st.booleans()))


@st.composite
def _generated_draft(draw):
    """Build a freshly generated DraftModel (all GENERATED content).

    Titles come from the same pool so some sections match the existing draft
    (update path) and some are new (append path).
    """
    blocks: list[DraftBlock] = []
    n_sections = draw(st.integers(min_value=0, max_value=4))
    for _ in range(n_sections):
        blocks.append(draw(_heading_block()))
        n_body = draw(st.integers(min_value=0, max_value=3))
        for _ in range(n_body):
            blocks.append(draw(_paragraph_block(manual=False)))
    return DraftModel(blocks=blocks, trailing_newline=draw(st.booleans()))


# =========================================================================== #
# Property 21: Konten_Manual dipertahankan utuh
# =========================================================================== #
# Feature: automated-writing-workflow, Property 21: Konten_Manual dipertahankan utuh
# Validates: Requirements 8.2
@settings(max_examples=200, deadline=None)
@given(existing=_existing_draft(), generated=_generated_draft())
def test_manual_content_preserved_intact(existing, generated):
    # Snapshot every Konten_Manual block before merging: identity + content.
    manual_before = [b for b in existing.blocks if is_manual_content(b)]
    snapshot = [(id(b), list(b.lines)) for b in manual_before]

    merged, _findings = merge(existing, generated)

    merged_by_id = {id(b): b for b in merged.blocks}

    for block_id, original_lines in snapshot:
        # Present: not deleted, not overwritten.
        assert block_id in merged_by_id, (
            "a Konten_Manual block was dropped by merge (deleted/overwritten)"
        )
        kept = merged_by_id[block_id]
        # Content unchanged: identical lines, still marked MANUAL.
        assert kept.lines == original_lines, (
            f"Konten_Manual content was modified: {kept.lines!r} "
            f"!= {original_lines!r}"
        )
        assert kept.kind == BlockKind.MANUAL, (
            "a Konten_Manual block lost its MANUAL kind after merge"
        )

    # The count of manual blocks never decreases (nothing silently removed).
    manual_after = [b for b in merged.blocks if is_manual_content(b)]
    assert len(manual_after) >= len(manual_before)
