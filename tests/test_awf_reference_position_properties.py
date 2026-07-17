"""Property-based test for the position of a Rujukan_Objek within narrative.

Spec: .kiro/specs/automated-writing-workflow

Covers task 8.2 (Property 9) against the PURE ``is_valid_reference_position``
predicate exposed by ``skills/scripts/alur_penulisan/figure_table.py``.

Deciding whether a "Gambar x.y" / "Tabel x.y" mention sits at a valid position
is a pure ``(text, index) -> bool`` transformation, so 100+ Hypothesis
iterations are cheap and touch no disk.

This is a brand-new, uniquely named file. It does NOT modify or overwrite any
other test suite.
"""
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import is_valid_reference_position from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.figure_table import is_valid_reference_position  # noqa: E402


# --------------------------------------------------------------------------- #
# Vocabulary building blocks.
# --------------------------------------------------------------------------- #
_TERMINATORS = [".", "?", "!"]

# Neutral narrative words. None of them is a sentence terminator on its own.
_WORDS = [
    "sistem", "platform", "arsitektur", "modul", "komponen", "navigasi",
    "kampus", "gedung", "fasilitas", "hasil", "pengujian", "menunjukkan",
    "seperti", "terlihat", "pada", "ditampilkan", "dijelaskan", "berikut",
    "yang", "dan", "tersebut", "sebagaimana", "digambarkan",
]

# The reference phrases (Rujukan_Objek) that get inserted into the text.
_REFERENCES = ["Gambar 2.1", "Tabel 3.4", "Gambar 4.10", "Tabel 1.2"]


def _oracle(prefix: str) -> bool:
    """Independent reimplementation of Requirement 4.1's position rule.

    A reference is valid iff, after ignoring trailing whitespace, the text that
    precedes it is non-empty (not the paragraph start) and does not end with a
    sentence terminator (``.`` ``?`` ``!``).
    """
    stripped = prefix.rstrip()
    if stripped == "":
        return False
    return stripped[-1] not in "".join(_TERMINATORS)


@st.composite
def _prefix(draw: st.DrawFn) -> str:
    """A narrative prefix that lands in one of three interesting categories:

    * empty / whitespace-only        -> paragraph start (expected invalid)
    * ends with a sentence terminator -> just after "." "?" "!" (invalid)
    * ends with an ordinary word      -> valid mid-paragraph position
    """
    category = draw(st.sampled_from(["empty", "terminator", "normal"]))

    if category == "empty":
        # Nothing, or only whitespace, before the reference.
        return draw(st.sampled_from(["", " ", "  ", "\t", " \n ", "\n\n"]))

    words = draw(st.lists(st.sampled_from(_WORDS), min_size=1, max_size=12))
    body = " ".join(words)

    if category == "terminator":
        body += draw(st.sampled_from(_TERMINATORS))

    # Optional trailing whitespace between the prefix and the reference; the
    # rule must ignore it in every category.
    body += draw(st.sampled_from(["", " ", "  ", "\t", " \n"]))
    return body


@st.composite
def reference_scenario(draw: st.DrawFn):
    """Build ``(sentence, index, expected)`` exercising Property 9.

    The reference phrase is inserted at ``index == len(prefix)`` and an optional
    tail is appended so the phrase can sit anywhere in the paragraph.
    """
    prefix = draw(_prefix())
    phrase = draw(st.sampled_from(_REFERENCES))

    tail_words = draw(st.lists(st.sampled_from(_WORDS), min_size=0, max_size=8))
    tail = (" " + " ".join(tail_words)) if tail_words else ""

    sentence = f"{prefix}{phrase}{tail}"
    index = len(prefix)
    expected = _oracle(prefix)
    return sentence, index, expected


# --------------------------------------------------------------------------- #
# Property 9
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 9: Posisi valid Rujukan_Objek
@settings(max_examples=200)
@given(scenario=reference_scenario())
def test_property_9_valid_reference_position(scenario) -> None:
    """Property 9: Posisi valid Rujukan_Objek.

    Untuk setiap Rujukan_Objek (Gambar x.y / Tabel x.y) yang dituliskan, frasa
    rujukan tidak berada di awal paragraf dan tidak tepat setelah tanda akhir
    kalimat (titik, tanda tanya, atau tanda seru), mengabaikan whitespace di
    antaranya.

    Validates: Requirements 4.1
    """
    sentence, index, expected = scenario

    assert is_valid_reference_position(sentence, index) is expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
