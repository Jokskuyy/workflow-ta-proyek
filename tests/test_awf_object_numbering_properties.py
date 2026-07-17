"""Property-based test for FigureTableManager numbering (automated-writing-workflow).

Spec: .kiro/specs/automated-writing-workflow

Covers task 8.3 (Property 10) against the PURE numbering helper exposed by
``skills/scripts/alur_penulisan/figure_table.py``:

  number_objects(draft) -> (DraftModel, list[Finding])

A draft is built from random chapters ("# BAB <roman/arabic>" headings) with an
interleaved sequence of Gambar/Tabel captions (paragraphs starting with the
keyword ``Gambar``/``Tabel``). The property asserts that every object is numbered
``x.y`` where ``x`` is the chapter number the object lives in and ``y`` is the
1-based reading-order sequence within that chapter — reset to 1 at each new
chapter and counted separately for Gambar and Tabel (Requirements 4.2, 4.3).

Numbering is a pure text transformation over an in-memory DraftModel, so 100+
Hypothesis iterations are cheap. Nothing here touches disk. This is a brand-new
file.
"""
import re
import string
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the FigureTableManager from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.draft_model import (  # noqa: E402
    DraftBlockType,
    DraftModel,
)
from alur_penulisan.figure_table import number_objects  # noqa: E402

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX"}

# Matches a caption's leading token after (re)numbering: "Gambar 2.1 ..." etc.
_CAPTION_NUM_RE = re.compile(r"^\s*(?P<kw>Gambar|Tabel)\s+(?P<num>\d+\.\d+)\b")

# Description words: plain letters so they never look like a number or interfere
# with caption/keyword detection at the start of a line.
_WORD = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=6)
_DESC = st.lists(_WORD, min_size=1, max_size=3).map(lambda ws: " ".join(ws))


@st.composite
def drafts_with_captions(draw: st.DrawFn):
    """Build ``(markdown_text, expected)``.

    ``expected`` is the list of ``(kind, "x.y")`` numbers the captions SHOULD
    receive, in document (reading) order. Chapters use unique numbers so each
    chapter is a distinct reset boundary; the heading is rendered as either a
    Roman or Arabic numeral (both are valid "# BAB ..." forms).
    """
    n_chapters = draw(st.integers(min_value=1, max_value=4))
    chapter_numbers = draw(
        st.lists(
            st.integers(min_value=1, max_value=9),
            min_size=n_chapters,
            max_size=n_chapters,
            unique=True,
        )
    )

    lines: list[str] = []
    expected: list[tuple[str, str]] = []
    counters: dict[tuple[int, str], int] = {}

    for chapter in chapter_numbers:
        # Randomly render the chapter number as Roman or Arabic; the parsed
        # value equals ``chapter`` either way.
        use_roman = draw(st.booleans())
        label = _ROMAN[chapter] if use_roman else str(chapter)
        lines.append(f"# BAB {label} Judul Bab")
        lines.append("")

        n_objects = draw(st.integers(min_value=0, max_value=5))
        for _ in range(n_objects):
            kind = draw(st.sampled_from(["Gambar", "Tabel"]))
            desc = draw(_DESC)

            key = (chapter, kind)
            seq_y = counters.get(key, 0) + 1
            counters[key] = seq_y
            expected.append((kind, f"{chapter}.{seq_y}"))

            # Caption paragraph (its own block, separated by blank lines). The
            # caption is written WITHOUT a number so numbering must assign one.
            lines.append(f"{kind} {desc}")
            lines.append("")

        # Occasionally add a plain narrative paragraph (not a caption) to make
        # sure non-caption blocks never receive a number.
        if draw(st.booleans()):
            filler = draw(_DESC)
            lines.append(f"Narasi {filler} pada bab ini.")
            lines.append("")

    return "\n".join(lines), expected


def _extract_caption_numbers(draft: DraftModel) -> list[tuple[str, str]]:
    """Return ``(kind, "x.y")`` for every caption paragraph, in document order."""
    result: list[tuple[str, str]] = []
    for block in draft.blocks:
        if block.block_type not in (DraftBlockType.PARAGRAPH, DraftBlockType.PREAMBLE):
            continue
        first = next((l for l in block.lines if l.strip() != ""), "")
        match = _CAPTION_NUM_RE.match(first)
        if match:
            result.append((match.group("kw"), match.group("num")))
    return result


# --------------------------------------------------------------------------- #
# Property 10
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 10: Penomoran Gambar dan Tabel mengikuti reading order per bab
@settings(max_examples=200)
@given(scenario=drafts_with_captions())
def test_property_10_object_numbering_follows_reading_order_per_chapter(scenario) -> None:
    """Property 10: Penomoran Gambar dan Tabel mengikuti reading order per bab.

    Untuk setiap Berkas_Draf, nomor setiap Gambar/Tabel berformat x.y dengan x
    adalah nomor bab tempat objek berada dan y adalah urutan kemunculan objek
    pada bab tersebut (mulai dari 1, bertambah 1 mengikuti reading order);
    penghitung y di-reset ke 1 pada setiap bab baru dan dihitung terpisah untuk
    Gambar dan untuk Tabel.

    Validates: Requirements 4.2, 4.3
    """
    text, expected = scenario
    draft = DraftModel.from_markdown(text)

    numbered, _findings = number_objects(draft)
    actual = _extract_caption_numbers(numbered)

    # Same set of captions, same reading order, exactly the numbers we expect.
    assert actual == expected

    # Independent structural re-derivation of the expectation: every number is
    # "x.y"; ``y`` is the running per-chapter, per-kind counter that resets at 1
    # for each distinct chapter and is tracked separately for Gambar vs Tabel.
    seen: dict[tuple[str, str], int] = {}
    for kind, number in actual:
        x, y = number.split(".")

        # Format: exactly "x.y" with positive integer components.
        assert x.isdigit() and y.isdigit()
        assert int(x) >= 1 and int(y) >= 1

        counter_key = (x, kind)
        expected_y = seen.get(counter_key, 0) + 1
        seen[counter_key] = expected_y

        # ``y`` increases by exactly 1 in reading order within (chapter, kind),
        # starting from 1 — i.e. the counter resets per chapter and per kind.
        assert int(y) == expected_y


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
