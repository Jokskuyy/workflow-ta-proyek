"""Property-based tests for the SectionContentWriter of the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers task 6.3 (Property 5) against the PURE SectionContentWriter helpers exposed
by ``skills/scripts/alur_penulisan/content_writer.py``:

  mark_paragraph_citations, MISSING_CITATION_MARKER, find_citations,
  write_theory_subchapter, EMPTY_BIBLIOGRAPHY.

Citation marking is a pure text-in/text-out transformation, so 100+ Hypothesis
iterations are cheap. The existing pipeline test suites are NOT modified; this is
a brand-new file. Nothing here touches disk.
"""
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the SectionContentWriter from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.content_writer import (  # noqa: E402
    EMPTY_BIBLIOGRAPHY,
    MISSING_CITATION_MARKER,
    BibliographyResult,
    find_citations,
    mark_paragraph_citations,
    write_theory_subchapter,
)
from alur_penulisan.models import Level, Paragraph, SkeletonEntry  # noqa: E402


# --------------------------------------------------------------------------- #
# Strategy: factual claims that are NOT common knowledge, NOT the author's own
# observation, and carry NO APA citation.
# --------------------------------------------------------------------------- #
# A neutral vocabulary of plain words. None of them contain the author-observation
# cues (lampiran, hasil kuesioner, observasi penulis, ...) nor any of the marker /
# citation punctuation, so a claim built from them is guaranteed to require a
# citation and to have none.
_WORDS = [
    "sistem", "platform", "arsitektur", "modul", "komponen", "navigasi",
    "kampus", "gedung", "fasilitas", "basis", "data", "layanan", "antarmuka",
    "pengguna", "peta", "virtual", "tiga", "dimensi", "mesin", "render",
    "menyediakan", "menampilkan", "memproses", "mengelola", "meningkatkan",
    "akurasi", "kinerja", "efisiensi", "integrasi", "informasi", "publik",
]


@st.composite
def factual_claims(draw: st.DrawFn) -> str:
    """Generate a non-empty factual claim with no citation and no observation cue.

    The claim is a sentence built from a neutral vocabulary; it never contains an
    author-year citation ``(Nama Tahun)`` (no parentheses/years), never contains the
    Penanda_Sitasi_Kurang, and never matches the author-observation exemption.
    """
    words = draw(st.lists(st.sampled_from(_WORDS), min_size=1, max_size=20))
    sentence = " ".join(words)
    if draw(st.booleans()):
        sentence += "."
    # Optional random edge whitespace to exercise the rstrip behaviour.
    lead = " " * draw(st.integers(min_value=0, max_value=3))
    trail = " " * draw(st.integers(min_value=0, max_value=3))
    return f"{lead}{sentence}{trail}"


def _strip_markers(text: str) -> str:
    """Remove every Penanda_Sitasi_Kurang and normalize whitespace for comparison."""
    return " ".join(text.replace(MISSING_CITATION_MARKER, "").split())


def test_citation_parser_accepts_no_comma_and_rejects_legacy_comma():
    assert len(find_citations("Definisi ini didukung (Nama Penulis 2024).")) == 1
    assert find_citations("Definisi ini memakai format lama (Nama Penulis, 2024).") == []


# --------------------------------------------------------------------------- #
# Property 5
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 5: Penandaan klaim tanpa sitasi tanpa penghapusan teks
@settings(max_examples=200)
@given(claim=factual_claims())
def test_property_5_uncited_claim_marked_without_deletion(claim: str) -> None:
    """Property 5: Penandaan klaim tanpa sitasi tanpa penghapusan teks.

    Untuk setiap klaim faktual yang bukan pengetahuan umum dan bukan observasi
    penulis sendiri serta belum memiliki Sitasi_APA, hasilnya menambahkan
    Penanda_Sitasi_Kurang pada posisi klaim dan mempertahankan seluruh teks klaim
    tanpa menghapusnya.

    Validates: Requirements 2.3, 2.4
    """
    # Precondition sanity: the generated claim really has no citation and no marker.
    assert find_citations(claim) == []
    assert MISSING_CITATION_MARKER not in claim

    paragraph = Paragraph(text=claim, is_definition=False)
    marked, findings = mark_paragraph_citations(paragraph, EMPTY_BIBLIOGRAPHY, "2.3.1 ¶1")

    # 1. The Penanda_Sitasi_Kurang was added at the claim.
    assert MISSING_CITATION_MARKER in marked.text, (
        "klaim faktual tanpa sitasi harus ditandai [BUTUH SITASI]"
    )

    # 2. A MISSING_CITATION finding is reported for the claim.
    assert any(f.kind.value == "missing_citation" for f in findings), (
        "penandaan klaim harus menghasilkan Finding MISSING_CITATION"
    )

    # 3. The entire original claim text is preserved — nothing deleted. Removing
    #    the inserted marker recovers the original claim content verbatim.
    assert _strip_markers(marked.text) == _strip_markers(claim), (
        "teks klaim harus dipertahankan tanpa penghapusan"
    )

    # 4. Idempotent: re-marking already-marked text adds no second marker.
    remarked, _ = mark_paragraph_citations(marked, EMPTY_BIBLIOGRAPHY, "2.3.1 ¶1")
    assert remarked.text.count(MISSING_CITATION_MARKER) == 1, (
        "penandaan harus idempoten (tidak menambah penanda ganda)"
    )


# Feature: automated-writing-workflow, Property 5: Penandaan klaim tanpa sitasi tanpa penghapusan teks
@settings(max_examples=200)
@given(
    claims=st.lists(factual_claims(), min_size=1, max_size=6),
    title=st.sampled_from(["UAT", "Black Box Testing", "ERD", "NavMesh", "Pengujian"]),
)
def test_property_5_uncited_claims_marked_in_subchapter(claims: "list[str]", title: str) -> None:
    """Property 5 at the sub-chapter level via ``write_theory_subchapter``.

    Every uncited factual claim in the composed Sub_Bab_Teori is marked with
    ``[BUTUH SITASI]`` while its text is preserved (no deletion), including the
    first (definition) paragraph when it lacks a validated citation
    (Requirement 2.4).

    Validates: Requirements 2.3, 2.4
    """
    entry = SkeletonEntry(
        entry_id="2.3.1",
        numbering="2.3.1",
        title=title,
        level=Level.SUBSUBBAB,
        owner_role="iman",
    )
    drafts = [Paragraph(text=c, is_definition=False) for c in claims]

    block, _findings = write_theory_subchapter(entry, facts=None, bib=EMPTY_BIBLIOGRAPHY, drafts=drafts)

    assert len(block.paragraphs) == len(claims)
    for original, produced in zip(claims, block.paragraphs):
        # Each uncited claim (including the definition paragraph) is flagged...
        assert MISSING_CITATION_MARKER in produced.text, (
            "setiap klaim tanpa sitasi harus ditandai [BUTUH SITASI]"
        )
        # ...and its original text is preserved verbatim (nothing deleted).
        assert _strip_markers(original) in _strip_markers(produced.text), (
            "teks klaim harus dipertahankan tanpa penghapusan"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
