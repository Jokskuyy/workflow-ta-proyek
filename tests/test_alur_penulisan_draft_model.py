"""Unit + property tests for the Alur_Penulisan data models and DraftModel.

Task 1.2 (automated-writing-workflow):
  * ``DraftModel`` parses then re-serializes Markdown text without losing
    structure (lossless round-trip).
  * ``BlockKind.MANUAL`` block marking is preserved on the model.

Validates: Requirements 7.2 (draft stays compatible / structure preserved) and
8.2 (Konten_Manual preserved untouched).

Import setup mirrors the other tests in this directory: the ``skills/scripts``
folder is placed on ``sys.path`` so the ``alur_penulisan`` package resolves.
"""
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "scripts"
if str(SKILLS) not in sys.path:
    sys.path.insert(0, str(SKILLS))

from alur_penulisan.draft_model import (  # noqa: E402
    DraftBlock,
    DraftBlockType,
    DraftModel,
)
from alur_penulisan.models import BlockKind  # noqa: E402


# --------------------------------------------------------------------------- #
# Example fixtures
# --------------------------------------------------------------------------- #
SAMPLE_DRAFT = """# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Ini adalah paragraf pertama dengan penjelasan (Penulis, 2024).

   1. Item pertama
   2. Item kedua
      a. Sub item

[TABLE]
| Kolom A | Kolom B |
| --- | --- |
| 1 | 2 |
[/TABLE]

| H1 | H2 |
| :-- | --: |
| a | b |

---

# DAFTAR PUSTAKA

Penulis, A. (2024). Judul. Penerbit.
"""


# --------------------------------------------------------------------------- #
# Unit tests: round-trip preserves structure
# --------------------------------------------------------------------------- #
def test_round_trip_sample_draft_is_lossless():
    model = DraftModel.from_markdown(SAMPLE_DRAFT)
    assert model.to_markdown() == SAMPLE_DRAFT


def test_round_trip_empty_string():
    model = DraftModel.from_markdown("")
    assert model.to_markdown() == ""


def test_round_trip_preserves_trailing_newline():
    text = "# BAB I PENDAHULUAN\n"
    assert DraftModel.from_markdown(text).to_markdown() == text
    text_no_nl = "# BAB I PENDAHULUAN"
    assert DraftModel.from_markdown(text_no_nl).to_markdown() == text_no_nl


def test_round_trip_preserves_blank_line_runs():
    text = "# BAB I\n\n\nParagraf setelah dua baris kosong.\n"
    assert DraftModel.from_markdown(text).to_markdown() == text


def test_structure_is_classified_into_expected_block_types():
    model = DraftModel.from_markdown(SAMPLE_DRAFT)
    types = {b.block_type for b in model.blocks}
    assert DraftBlockType.HEADING in types
    assert DraftBlockType.LIST in types
    assert DraftBlockType.TABLE in types
    assert DraftBlockType.PIPE_TABLE in types
    assert DraftBlockType.PAGE_BREAK in types
    # The bibliography heading is detected as such.
    assert any(
        b.block_type == DraftBlockType.HEADING and b.meta.get("is_bibliography")
        for b in model.blocks
    )


def test_headings_accessor_returns_all_headings_in_order():
    model = DraftModel.from_markdown(SAMPLE_DRAFT)
    heading_texts = [b.meta["text"] for b in model.headings()]
    assert heading_texts == [
        "BAB I PENDAHULUAN",
        "1.1 Latar Belakang",
        "DAFTAR PUSTAKA",
    ]


# --------------------------------------------------------------------------- #
# Unit tests: BlockKind.MANUAL marking is preserved on the model
# --------------------------------------------------------------------------- #
def test_manual_block_marking_is_preserved_on_model():
    model = DraftModel.from_markdown(SAMPLE_DRAFT)
    # Mark the first paragraph block as Konten_Manual.
    para = next(b for b in model.blocks if b.block_type == DraftBlockType.PARAGRAPH)
    para.kind = BlockKind.MANUAL

    manual = model.manual_blocks()
    assert para in manual
    assert all(b.kind == BlockKind.MANUAL for b in manual)
    # The manual mark does not affect the serialized text (round-trip intact).
    assert model.to_markdown() == SAMPLE_DRAFT


def test_default_block_kind_is_generated():
    model = DraftModel.from_markdown(SAMPLE_DRAFT)
    assert all(b.kind == BlockKind.GENERATED for b in model.blocks)
    assert model.manual_blocks() == []


def test_manual_marking_survives_reserialize_and_reparse_text():
    # Marking is a model-level attribute; text round-trips and re-parsing keeps
    # the same block structure even though kind resets to GENERATED on parse.
    model = DraftModel.from_markdown(SAMPLE_DRAFT)
    for b in model.blocks:
        b.kind = BlockKind.MANUAL
    assert len(model.manual_blocks()) == len(model.blocks)
    reparsed = DraftModel.from_markdown(model.to_markdown())
    assert len(reparsed.blocks) == len(model.blocks)


# --------------------------------------------------------------------------- #
# Property test: round-trip is lossless for arbitrary Markdown-like text
# --------------------------------------------------------------------------- #
# Build lines that exercise the different block grammars the parser recognises.
_line_strategies = st.one_of(
    st.just(""),                                   # blank line
    st.just("---"),                                # page break
    st.just("# BAB I PENDAHULUAN"),                # bab heading
    st.just("## 1.1 Sub Bab"),                     # sub heading
    st.just("### 1.1.1 Sub sub"),                  # sub-sub heading
    st.just("# DAFTAR PUSTAKA"),                   # bibliography heading
    st.just("   1. Item satu"),                    # list item level 1
    st.just("      a. Item huruf"),                # list item level 2
    st.just("[TABLE]"),                            # table open
    st.just("[/TABLE]"),                           # table close
    st.just("| A | B |"),                          # pipe row
    st.just("| --- | --- |"),                      # pipe separator
    st.just("```"),                                # code fence
    st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs", "Cc"),
            blacklist_characters="\n\r",
        ),
        min_size=1,
        max_size=40,
    ),                                             # arbitrary paragraph text
)


@settings(max_examples=200)
@given(
    lines=st.lists(_line_strategies, max_size=25),
    trailing_newline=st.booleans(),
)
def test_round_trip_is_lossless_property(lines, trailing_newline):
    text = "\n".join(lines)
    if trailing_newline and text != "":
        text += "\n"
    model = DraftModel.from_markdown(text)
    assert model.to_markdown() == text


@settings(max_examples=200)
@given(
    lines=st.lists(_line_strategies, max_size=25),
    trailing_newline=st.booleans(),
)
def test_manual_marking_never_changes_serialized_text_property(lines, trailing_newline):
    text = "\n".join(lines)
    if trailing_newline and text != "":
        text += "\n"
    model = DraftModel.from_markdown(text)
    for b in model.blocks:
        b.kind = BlockKind.MANUAL
    # Every block is now MANUAL and the text is byte-for-byte identical.
    assert len(model.manual_blocks()) == len(model.blocks)
    assert model.to_markdown() == text


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-v"]))
