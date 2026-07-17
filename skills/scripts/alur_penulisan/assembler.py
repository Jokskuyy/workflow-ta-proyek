"""Assembler — assemble skeleton entries and their content into a draft.

This module implements section "9. Assembler" of the design document
(``.kiro/specs/automated-writing-workflow/design.md``). It is a **pure**
component: it takes a :class:`~alur_penulisan.models.Skeleton` plus a mapping
from ``entry_id`` to :class:`~alur_penulisan.models.ContentBlock`, and returns a
new :class:`~alur_penulisan.draft_model.DraftModel` together with a list of
:class:`~alur_penulisan.models.Finding`. It never touches disk.

Contract (Requirements 7.1, 7.3, 7.4, 7.5):

* **Order & depth (7.1)** — chapters/sub-chapters are laid out in exactly the
  order and at exactly the depth of the Kerangka_Bab: ``Skeleton.entries`` is the
  canonical reading order, and each entry's :class:`~alur_penulisan.models.Level`
  determines the heading depth (``#`` per level).
* **Exactly once on success (7.5)** — a successful assembly emits every skeleton
  entry exactly one time.
* **Missing content (7.3)** — if one or more skeleton entries have no associated
  content, assembly stops and raises :class:`AssemblyError` naming every entry
  whose content is missing, **without** producing a partial draft.
* **Orphan content (7.4)** — if some content has no matching skeleton entry,
  assembly stops and raises :class:`AssemblyError` naming the orphan content,
  **without** producing a partial draft.

Both validation checks run *before* any :class:`DraftModel` is constructed, so a
failed assembly can never leak a partial draft (design.md "Galat validasi
perakitan").

The emitted Markdown (headings + blank separators + paragraph blocks) stays
compatible with ``skills/scripts/merge_draft_to_docx.py`` (Requirement 7.2); this
module does not modify the format stage.
"""

from __future__ import annotations

from .draft_model import DraftBlock, DraftBlockType, DraftModel
from .exceptions import AssemblyError
from .models import ContentBlock, Finding, Skeleton, SkeletonEntry

# Type alias for readability (mirrors the design signature ``dict[EntryId, ...]``).
EntryId = str


def _heading_line(entry: SkeletonEntry) -> str:
    """Build the Markdown heading line for a skeleton entry.

    Depth is encoded by repeating ``#`` ``entry.level.value`` times so the
    assembled heading preserves the Kerangka_Bab depth (Requirement 7.1). The
    displayed hierarchical numbering is prefixed to the title unless the title
    already begins with it (avoids doubling for entries whose canonical title
    already carries its number, e.g. "BAB I PENDAHULUAN").
    """
    hashes = "#" * entry.level.value
    title = entry.title.strip()
    numbering = entry.numbering.strip()
    if numbering and not title.startswith(numbering):
        text = f"{numbering} {title}"
    else:
        text = title
    return f"{hashes} {text}".rstrip()


def _heading_block(entry: SkeletonEntry) -> DraftBlock:
    """Create a HEADING :class:`DraftBlock` for a skeleton entry."""
    line = _heading_line(entry)
    level = entry.level.value
    heading_text = line[level:].strip()
    return DraftBlock(
        DraftBlockType.HEADING,
        [line],
        meta={"level": level, "text": heading_text, "is_bibliography": False},
    )


def _blank_block() -> DraftBlock:
    """A single blank-line separator block (keeps output valid Markdown)."""
    return DraftBlock(DraftBlockType.BLANK, [""])


def assemble(
    skeleton: Skeleton,
    contents: "dict[EntryId, ContentBlock]",
) -> "tuple[DraftModel, list[Finding]]":
    """Assemble a skeleton and its content blocks into a :class:`DraftModel`.

    Args:
        skeleton: the Kerangka_Bab whose entry order/depth drives the layout.
        contents: mapping ``entry_id -> ContentBlock`` supplying each entry's
            body. Every skeleton entry must have an entry here, and every entry
            in this mapping must correspond to a skeleton entry.

    Returns:
        A tuple ``(draft, findings)``. On success ``draft`` contains every
        skeleton entry exactly once, in skeleton order and at skeleton depth,
        and ``findings`` is an empty list.

    Raises:
        AssemblyError: if any skeleton entry has no content (``missing_entries``)
            or any content has no matching skeleton entry (``orphan_contents``).
            In both cases no partial draft is produced.
    """
    entry_ids = [entry.entry_id for entry in skeleton.entries]
    entry_id_set = set(entry_ids)
    content_keys = set(contents.keys())

    # --- Validation (runs before any draft is built) --------------------- #
    # Requirement 7.3: skeleton entries with no associated content, in
    # skeleton order (deduplicated while preserving first appearance).
    missing_seen: set[str] = set()
    missing_entries: list[str] = []
    for entry_id in entry_ids:
        if entry_id not in content_keys and entry_id not in missing_seen:
            missing_seen.add(entry_id)
            missing_entries.append(entry_id)

    # Requirement 7.4: content with no matching skeleton entry.
    orphan_contents = sorted(content_keys - entry_id_set)

    if missing_entries or orphan_contents:
        parts: list[str] = []
        if missing_entries:
            parts.append(
                "entri Kerangka_Bab tanpa konten: " + ", ".join(missing_entries)
            )
        if orphan_contents:
            parts.append("konten yatim tanpa entri padanan: " + ", ".join(orphan_contents))
        message = (
            "Perakitan dihentikan tanpa menghasilkan Berkas_Draf sebagian — "
            + "; ".join(parts)
        )
        raise AssemblyError(
            message,
            missing_entries=tuple(missing_entries),
            orphan_contents=tuple(orphan_contents),
        )

    # --- Build the draft (all entries valid) ----------------------------- #
    blocks: list[DraftBlock] = []
    for entry in skeleton.entries:
        blocks.append(_heading_block(entry))
        blocks.append(_blank_block())

        block = contents[entry.entry_id]
        for paragraph in block.paragraphs:
            para_lines = paragraph.text.split("\n")
            blocks.append(
                DraftBlock(
                    DraftBlockType.PARAGRAPH,
                    para_lines,
                    kind=block.kind,
                )
            )
            blocks.append(_blank_block())

    draft = DraftModel(blocks=blocks, trailing_newline=True)
    findings: list[Finding] = []
    return draft, findings
