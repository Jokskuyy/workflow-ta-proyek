"""Property test for the IdempotentMerger's different-skeleton union (R8.4) of
the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 23: Penggabungan kerangka berbeda bersifat union yang
mempertahankan konten lama** — for every pair of an existing draft structure and
a differing current-run Kerangka_Bab, the result is a *union* of the entries in
which only chapters / sub-chapters that do not yet exist are appended, while
chapters that already exist keep their content and their Konten_Manual
(Requirement 8.4: "IF Kerangka_Bab jalan saat ini berbeda dengan struktur
Berkas_Draf, THEN THE Alur_Penulisan SHALL menggabungkan keduanya secara union:
menambahkan hanya entri baru dan mempertahankan bab lama beserta
Konten_Manual-nya.").

``merge`` is a pure transform (design.md §8 "IdempotentMerger"), so 100+
Hypothesis iterations are cheap.
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

from alur_penulisan.draft_model import (  # noqa: E402
    DraftBlock,
    DraftBlockType,
    DraftModel,
)
from alur_penulisan.merger import is_manual_content, merge  # noqa: E402
from alur_penulisan.models import BlockKind  # noqa: E402


# --------------------------------------------------------------------------- #
# Generators
# --------------------------------------------------------------------------- #
_TITLE_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


@st.composite
def _scenario(draw):
    """Build an (existing, generated) draft pair with *differing* skeletons.

    Titles are unique ignoring case. Each chapter is one of:

    * ``shared``        — present in both drafts (overlapping skeleton entry);
    * ``existing_only`` — present only in the existing draft (kept, must not be
                          dropped by the union);
    * ``generated_only``— present only in the current-run skeleton (a genuinely
                          new entry that must be appended).

    Existing chapters may carry a Konten_Manual body block (marker
    ``MANUAL_{idx}``); generated bodies are tagged ``BARU_{idx}``. The scenario
    guarantees at least one ``generated_only`` and one ``existing_only`` chapter
    so the two skeletons genuinely differ, and at least one manual block so the
    preservation clause is exercised.

    Returns ``(existing_model, generated_model, shared, existing_only,
    generated_only, manual_markers)``.
    """
    titles = draw(
        st.lists(
            st.text(alphabet=_TITLE_ALPHABET, min_size=3, max_size=8),
            min_size=3,
            max_size=7,
            unique_by=lambda t: t.casefold(),
        )
    )

    categories = [
        draw(st.sampled_from(["shared", "existing_only", "generated_only"]))
        for _ in titles
    ]
    # Force the skeletons to differ: at least one entry unique to each side.
    categories[0] = "existing_only"
    categories[1] = "generated_only"

    existing_blocks: list[DraftBlock] = []
    generated_blocks: list[DraftBlock] = []
    shared, existing_only, generated_only = [], [], []
    manual_markers: list[str] = []

    def _heading(level: int, title: str) -> DraftBlock:
        return DraftBlock(
            DraftBlockType.HEADING,
            [f"{'#' * level} {title}"],
            kind=BlockKind.GENERATED,
            meta={"level": level, "text": title},
        )

    for idx, (title, category) in enumerate(zip(titles, categories)):
        level = draw(st.sampled_from([1, 2]))

        if category in ("shared", "existing_only"):
            existing_blocks.append(_heading(level, title))
            # Optionally attach a Konten_Manual body that must be preserved.
            is_manual = draw(st.booleans())
            marker = f"{'MANUAL' if is_manual else 'LAMA'}_{idx}"
            existing_blocks.append(
                DraftBlock(
                    DraftBlockType.PARAGRAPH,
                    [f"Isi {marker} bab ini."],
                    kind=BlockKind.MANUAL if is_manual else BlockKind.GENERATED,
                )
            )
            if is_manual:
                manual_markers.append(marker)

        if category in ("shared", "generated_only"):
            generated_blocks.append(_heading(level, title))
            generated_blocks.append(
                DraftBlock(
                    DraftBlockType.PARAGRAPH,
                    [f"Isi BARU_{idx} bab ini."],
                    kind=BlockKind.GENERATED,
                )
            )

        if category == "shared":
            shared.append((level, title, idx))
        elif category == "existing_only":
            existing_only.append((level, title, idx))
        else:
            generated_only.append((level, title, idx))

    # Guarantee at least one Konten_Manual block so the preservation clause is
    # always exercised: convert the first existing chapter's body to MANUAL.
    if not manual_markers:
        for i, blk in enumerate(existing_blocks):
            if blk.block_type == DraftBlockType.PARAGRAPH:
                idx = int(blk.lines[0].split("_")[1].split(" ")[0])
                marker = f"MANUAL_{idx}"
                existing_blocks[i] = DraftBlock(
                    DraftBlockType.PARAGRAPH,
                    [f"Isi {marker} bab ini."],
                    kind=BlockKind.MANUAL,
                )
                manual_markers.append(marker)
                break

    existing_model = DraftModel(
        blocks=existing_blocks, trailing_newline=draw(st.booleans())
    )
    generated_model = DraftModel(
        blocks=generated_blocks, trailing_newline=draw(st.booleans())
    )
    return (
        existing_model,
        generated_model,
        shared,
        existing_only,
        generated_only,
        manual_markers,
    )


def _heading_keys(model: DraftModel):
    """Location keys (level, casefolded/trimmed title) for every heading."""
    return [
        (h.meta.get("level", 0), str(h.meta.get("text", "")).strip().casefold())
        for h in model.headings()
    ]


# =========================================================================== #
# Property 23: Penggabungan kerangka berbeda bersifat union yang mempertahankan
# konten lama
# =========================================================================== #
# Feature: automated-writing-workflow, Property 23: Penggabungan kerangka berbeda bersifat union yang mempertahankan konten lama
# Validates: Requirements 8.4
@settings(max_examples=200, deadline=None)
@given(data=_scenario())
def test_different_skeletons_merge_as_content_preserving_union(data):
    (
        existing,
        generated,
        shared,
        existing_only,
        generated_only,
        manual_markers,
    ) = data

    # Snapshot Konten_Manual blocks (identity + content) before merging.
    manual_before = [b for b in existing.blocks if is_manual_content(b)]
    manual_snapshot = [(id(b), list(b.lines)) for b in manual_before]

    merged, _findings = merge(existing, generated)

    key_counts = Counter(_heading_keys(merged))
    merged_keys = set(key_counts)

    def key(level, title):
        return (level, title.strip().casefold())

    existing_keys = set(_heading_keys(existing))
    generated_keys = set(_heading_keys(generated))

    # (1) UNION over the skeleton: the merged heading set is exactly the union
    # of the existing and generated heading sets — nothing extra, nothing lost.
    assert merged_keys == existing_keys | generated_keys, (
        f"merged skeleton {merged_keys} is not the union of existing "
        f"{existing_keys} and generated {generated_keys}"
    )

    # (2) Every entry appears exactly once (union adds new entries, never
    # duplicates existing or generated ones).
    for k, count in key_counts.items():
        assert count == 1, f"entry {k} appears {count} times, expected exactly 1"

    # (3) Existing-only chapters (absent from the current-run skeleton) are kept
    # together with their body — a union never drops old chapters.
    merged_text = merged.to_markdown()
    for level, title, idx in existing_only:
        assert key(level, title) in merged_keys, (
            f"existing-only chapter {title!r} was dropped by the union"
        )

    # (4) Generated-only chapters (the genuinely new entries) are appended.
    for level, title, idx in generated_only:
        assert key(level, title) in merged_keys, (
            f"new chapter {title!r} was not appended by the union"
        )
        assert f"BARU_{idx}" in merged_text, (
            f"new chapter idx {idx} was appended without its content"
        )

    # (5) Konten_Manual is preserved verbatim (same object, same lines, still
    # marked MANUAL) — old chapters keep their manual content across the union.
    merged_by_id = {id(b): b for b in merged.blocks}
    for block_id, original_lines in manual_snapshot:
        assert block_id in merged_by_id, (
            "a Konten_Manual block was dropped by the union merge"
        )
        kept = merged_by_id[block_id]
        assert kept.lines == original_lines, (
            f"Konten_Manual content changed: {kept.lines!r} != {original_lines!r}"
        )
        assert kept.kind == BlockKind.MANUAL, (
            "a Konten_Manual block lost its MANUAL kind after the union merge"
        )
    for marker in manual_markers:
        assert merged_text.count(f"Isi {marker} bab ini.") == 1, (
            f"manual marker {marker!r} not preserved exactly once after merge"
        )
