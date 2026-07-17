"""IdempotentMerger — safely merge a freshly generated draft into an existing one.

This is a **pure** transformation component (design.md §8 "IdempotentMerger").
It reconciles a newly generated :class:`~alur_penulisan.draft_model.DraftModel`
with the draft already on disk so the workflow can be re-run any number of times
without duplicating or corrupting content:

* Konten_Manual (blocks marked :data:`~alur_penulisan.models.BlockKind.MANUAL`)
  is preserved verbatim — never overwritten, deleted, or reordered away
  (Requirement 8.2).
* A chapter / sub-chapter that already exists is updated *in place* (at the same
  location) so it still appears exactly once — no duplicate copy is created
  (Requirement 8.3).
* Merging two different skeletons is a **union**: only genuinely new chapters /
  sub-chapters are appended, while existing chapters keep their content and their
  Konten_Manual (Requirement 8.4).

Because updates keep the existing heading in its original position and only swap
the generated body, re-running on the same skeleton yields an identical
structure with no duplication (Requirement 8.1).

The merger works on the block-oriented :class:`DraftModel`. It never touches the
``.docx`` format pipeline; it only rearranges Markdown blocks, so the merged
draft stays compatible with ``skills/scripts/merge_draft_to_docx.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .draft_model import DraftBlock, DraftBlockType, DraftModel
from .models import BlockKind, ContentBlock, Finding


def is_manual_content(block: "ContentBlock | DraftBlock") -> bool:
    """Return ``True`` when ``block`` is Konten_Manual (``BlockKind.MANUAL``).

    Accepts either a :class:`~alur_penulisan.models.ContentBlock` (the data-model
    representation from design.md) or a :class:`~alur_penulisan.draft_model.DraftBlock`
    (the block used by :class:`DraftModel`); both carry a ``kind`` attribute.
    Manual content must be preserved untouched by :func:`merge` (Requirement 8.2).
    """
    return getattr(block, "kind", BlockKind.GENERATED) == BlockKind.MANUAL


# --------------------------------------------------------------------------- #
# Internal section model
# --------------------------------------------------------------------------- #
# A heading key identifies a chapter / sub-chapter for "same location" matching.
# It combines the heading level with a case-insensitive, whitespace-trimmed title
# so re-runs match the same entry regardless of incidental casing differences
# (Requirement 8.3). ``None`` denotes the preamble segment before the first
# heading (front matter), which has no key and is always kept verbatim.
HeadingKey = "tuple[int, str]"


@dataclass
class _Section:
    """A heading plus every block that follows it until the next heading.

    ``key is None`` marks the preamble segment (blocks before the first heading).
    """

    key: "tuple[int, str] | None"
    heading: "DraftBlock | None"
    body: list[DraftBlock] = field(default_factory=list)

    def all_blocks(self) -> list[DraftBlock]:
        """The section rendered back to a flat block list (heading first)."""
        if self.heading is None:
            return list(self.body)
        return [self.heading, *self.body]


def _heading_key(block: DraftBlock) -> "tuple[int, str]":
    """Compute the location key for a heading block (level + normalized title)."""
    level = block.meta.get("level", 0)
    text = str(block.meta.get("text", "")).strip().casefold()
    return (level, text)


def _split_sections(blocks: list[DraftBlock]) -> list[_Section]:
    """Split a flat block list into sections delimited by heading blocks.

    The first section (key ``None``) collects any preamble blocks that appear
    before the first heading. Every subsequent heading starts a new section that
    owns all following non-heading blocks up to the next heading.
    """
    sections: list[_Section] = []
    current = _Section(key=None, heading=None, body=[])
    for block in blocks:
        if block.block_type == DraftBlockType.HEADING:
            sections.append(current)
            current = _Section(key=_heading_key(block), heading=block, body=[])
        else:
            current.body.append(block)
    sections.append(current)
    return sections


def _update_section_in_place(existing: _Section, generated: _Section) -> list[DraftBlock]:
    """Update ``existing`` with ``generated``'s body, preserving Konten_Manual.

    The existing heading is kept (same location, so no duplicate is created —
    Requirement 8.3). Manual blocks in the existing body are preserved in their
    original relative order (Requirement 8.2). The generated body replaces the
    existing *generated* blocks, inserted at the position of the first generated
    block (or appended when the existing body held only manual content).
    """
    out: list[DraftBlock] = [existing.heading] if existing.heading is not None else []
    new_body = list(generated.body)
    inserted = False
    for block in existing.body:
        if is_manual_content(block):
            out.append(block)  # keep Konten_Manual untouched, in place
        elif not inserted:
            out.extend(new_body)  # swap the run of generated blocks in one shot
            inserted = True
        # subsequent existing generated blocks are dropped (superseded)
    if not inserted:
        out.extend(new_body)
    return out


def merge(existing: DraftModel, generated: DraftModel) -> "tuple[DraftModel, list[Finding]]":
    """Merge ``generated`` into ``existing`` idempotently.

    Returns the merged :class:`DraftModel` and a (currently empty) list of
    :class:`~alur_penulisan.models.Finding`. The merge:

    * keeps the preamble and every Konten_Manual block verbatim (Requirement 8.2);
    * updates chapters present in both drafts at their existing location so each
      appears exactly once (Requirements 8.1, 8.3);
    * appends only the chapters that exist solely in ``generated`` (union),
      preserving all existing chapters and their Konten_Manual (Requirement 8.4).
    """
    findings: list[Finding] = []

    existing_sections = _split_sections(existing.blocks)
    generated_sections = _split_sections(generated.blocks)

    # Index generated sections by key (first occurrence wins) while remembering
    # their order so newly added chapters are appended deterministically.
    gen_by_key: dict[tuple[int, str], _Section] = {}
    gen_order: list[tuple[int, str]] = []
    for seg in generated_sections:
        if seg.key is None:
            continue
        if seg.key not in gen_by_key:
            gen_by_key[seg.key] = seg
            gen_order.append(seg.key)

    existing_keys = {seg.key for seg in existing_sections if seg.key is not None}

    result_blocks: list[DraftBlock] = []
    updated_keys: set[tuple[int, str]] = set()

    for seg in existing_sections:
        if seg.key is None:
            # Preamble / front matter: always kept verbatim.
            result_blocks.extend(seg.all_blocks())
            continue

        gen_seg = gen_by_key.get(seg.key)
        heading_is_manual = seg.heading is not None and is_manual_content(seg.heading)

        if gen_seg is None or heading_is_manual or seg.key in updated_keys:
            # No matching generated section, a manually-authored section, or a
            # duplicate heading already updated once -> keep as-is (never
            # overwrite Konten_Manual, never re-inject to avoid duplication).
            result_blocks.extend(seg.all_blocks())
        else:
            result_blocks.extend(_update_section_in_place(seg, gen_seg))
            updated_keys.add(seg.key)

    # Union: append generated chapters that do not exist in the current draft.
    for key in gen_order:
        if key not in existing_keys:
            result_blocks.extend(gen_by_key[key].all_blocks())

    trailing_newline = existing.trailing_newline if existing.blocks else generated.trailing_newline
    merged = DraftModel(blocks=result_blocks, trailing_newline=trailing_newline)
    return merged, findings
