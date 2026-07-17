"""Property-based test for dangling object references (automated-writing-workflow).

Spec: .kiro/specs/automated-writing-workflow

Covers task 8.4 (Property 11) against the PURE FigureTableManager exposed by
``skills/scripts/alur_penulisan/figure_table.py``:

  number_objects(draft) -> (DraftModel, list[Finding])

A Rujukan_Objek ("Gambar x.y" / "Tabel x.y") that points to an object which was
never numbered / does not exist in the draft must be reported as
``Finding(FindingKind.DANGLING_REFERENCE)`` naming that reference, while the
surrounding narrative is preserved verbatim (Requirement 4.4).

The transformation is pure text-in/text-out over an in-memory ``DraftModel``, so
100+ Hypothesis iterations are cheap. This is a brand-new file; nothing here
touches disk (the DraftModel is built from Markdown text).
"""
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

from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.figure_table import number_objects  # noqa: E402
from alur_penulisan.models import FindingKind  # noqa: E402

# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #
_ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}

# A narrative word made of lowercase letters that can never be mistaken for a
# caption keyword ("gambar"/"tabel") nor swallow the reference token.
_WORD = st.text(alphabet=string.ascii_lowercase, min_size=2, max_size=8).filter(
    lambda w: "gambar" not in w and "tabel" not in w
)


@st.composite
def dangling_ref_drafts(draw: st.DrawFn):
    """Generate ``(markdown, refs)``.

    The draft holds one chapter heading and one paragraph per reference. Each
    paragraph places a ``Gambar x.y`` / ``Tabel x.y`` reference *mid-paragraph*
    (preceded by narrative text so it is a reference, not a caption). Because the
    draft contains **no captions**, every generated reference is dangling: it
    points to an object that does not exist in the draft.

    ``refs`` is the list of ``(kind, number, paragraph_text)`` tuples produced.
    """
    chapter = draw(st.integers(min_value=1, max_value=4))
    lines: list[str] = [f"# BAB {_ROMAN[chapter]} PENDAHULUAN", ""]

    n_refs = draw(st.integers(min_value=1, max_value=5))
    refs: list[tuple[str, str, str]] = []
    for _ in range(n_refs):
        kind = draw(st.sampled_from(["Gambar", "Tabel"]))
        x = draw(st.integers(min_value=1, max_value=9))
        y = draw(st.integers(min_value=1, max_value=9))
        number = f"{x}.{y}"

        prefix_words = draw(st.lists(_WORD, min_size=1, max_size=3))
        prefix = " ".join(prefix_words) + " "
        suffix_words = draw(st.lists(_WORD, min_size=0, max_size=3))
        suffix = (" " + " ".join(suffix_words)) if suffix_words else ""

        paragraph = f"{prefix}{kind} {number}{suffix}"
        refs.append((kind, number, paragraph))
        lines.append(paragraph)
        lines.append("")

    return "\n".join(lines), refs


# --------------------------------------------------------------------------- #
# Property 11
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 11: Rujukan objek menggantung dilaporkan tanpa menghapus narasi
@settings(max_examples=150)
@given(scenario=dangling_ref_drafts())
def test_property_11_dangling_reference_reported_without_deleting_narrative(scenario) -> None:
    """Property 11: Rujukan objek menggantung dilaporkan tanpa menghapus narasi.

    Untuk setiap Rujukan_Objek ke Gambar/Tabel yang belum bernomor atau tidak
    ada pada Berkas_Draf, hasilnya menghasilkan indikasi kesalahan yang menyebut
    rujukan tersebut dan mempertahankan narasi tanpa menghapusnya.

    Validates: Requirements 4.4
    """
    markdown, refs = scenario
    draft = DraftModel.from_markdown(markdown)

    numbered, findings = number_objects(draft)

    dangling = [f for f in findings if f.kind == FindingKind.DANGLING_REFERENCE]

    # (a) An error indication is produced naming each dangling reference.
    for kind, number, _paragraph in refs:
        phrase = f"{kind} {number}"
        assert any(
            phrase in f.detail for f in dangling
        ), f"missing DANGLING_REFERENCE naming {phrase!r}; findings={[f.detail for f in dangling]}"

    # (b) The narrative is preserved without deletion. With no captions to
    #     renumber, the output draft round-trips to the exact input text, so no
    #     reference text nor surrounding narrative is removed.
    output = numbered.to_markdown()
    assert output == markdown

    # Belt-and-suspenders: every reference phrase and its full paragraph survive.
    for kind, number, paragraph in refs:
        assert f"{kind} {number}" in output
        assert paragraph in output


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
