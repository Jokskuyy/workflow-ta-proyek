"""Property-based test for the cited definition paragraph of a Sub_Bab_Teori.

Spec: .kiro/specs/automated-writing-workflow

Covers task 6.2 (Property 4) against the PURE SectionContentWriter exposed by
``skills/scripts/alur_penulisan/content_writer.py``:

  write_theory_subchapter, has_cited_definition, find_citations,
  BibliographyResult, EMPTY_BIBLIOGRAPHY, MISSING_CITATION_MARKER.

Composing a theory sub-chapter is a pure text-in/text-out transformation, so
100+ Hypothesis iterations are cheap and touch no disk.

This is a brand-new, uniquely named file. It does NOT modify or overwrite
``test_alur_content_writer_properties.py`` (Property 5) nor any other suite.
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
    has_cited_definition,
    write_theory_subchapter,
)
from alur_penulisan.models import Level, Paragraph, SkeletonEntry  # noqa: E402


# --------------------------------------------------------------------------- #
# Vocabulary building blocks.
# --------------------------------------------------------------------------- #
# Theory sub-chapter titles (Sub_Bab_Teori concepts).
_TITLES = ["UAT", "Black Box Testing", "ERD", "NavMesh", "Pengujian", "RLS", "WebGL"]

# Author surnames and years for synthesised APA in-text citations.
_NAMES = ["Muharam", "Taurusta", "Nielsen", "Sommerville", "Pressman", "Sugiyono"]
_YEARS = ["2019", "2020", "2021", "2022", "2023", "2024"]

# Neutral vocabulary. None of these words contain parentheses, a 4-digit year,
# the Penanda_Sitasi_Kurang, nor any author-observation cue (lampiran, hasil
# kuesioner, observasi penulis, ...). A sentence built from them therefore has
# NO APA citation and requires one.
_WORDS = [
    "sistem", "platform", "arsitektur", "modul", "komponen", "navigasi",
    "kampus", "gedung", "fasilitas", "basis", "layanan", "antarmuka",
    "pengguna", "peta", "virtual", "tiga", "dimensi", "mesin", "render",
    "menyediakan", "menampilkan", "memproses", "mengelola", "meningkatkan",
    "akurasi", "kinerja", "efisiensi", "integrasi", "informasi", "publik",
    "adalah", "sebuah", "metode", "teknik", "proses", "pendekatan", "konsep",
]


@st.composite
def _plain_sentence(draw: st.DrawFn) -> str:
    """A non-empty sentence with no citation, no marker, no observation cue."""
    words = draw(st.lists(st.sampled_from(_WORDS), min_size=1, max_size=15))
    sentence = " ".join(words)
    if draw(st.booleans()):
        sentence += "."
    return sentence


@st.composite
def definition_scenario(draw: st.DrawFn):
    """Generate a (entry, drafts, bib) triple exercising Property 4.

    The scenarios cover the full input space of a composed Sub_Bab_Teori:

    * ``drafts=None`` -> a generated definition scaffold (never fabricates a
      source, so its first paragraph must be flagged ``[BUTUH SITASI]``).
    * definition drafts WITH an APA citation whose source IS in the
      bibliography (a validated, bibliography-backed citation).
    * definition drafts WITH an APA citation whose source is NOT in the
      bibliography (must be flagged).
    * definition drafts WITHOUT any citation (must be flagged).

    Extra trailing claim paragraphs (with no citation) may be added to ensure
    the definition remains the *only* definition paragraph at index 0.
    """
    title = draw(st.sampled_from(_TITLES))
    entry = SkeletonEntry(
        entry_id="2.3.1",
        numbering="2.3.1",
        title=title,
        level=Level.SUBSUBBAB,
        owner_role="iman",
    )

    use_scaffold = draw(st.booleans())
    if use_scaffold:
        # No drafts -> content_writer synthesises a definition scaffold.
        return entry, None, EMPTY_BIBLIOGRAPHY

    body = draw(_plain_sentence())
    include_citation = draw(st.booleans())

    bib = EMPTY_BIBLIOGRAPHY
    if include_citation:
        name = draw(st.sampled_from(_NAMES))
        year = draw(st.sampled_from(_YEARS))
        et_al = draw(st.booleans())
        author = f"{name} et al." if et_al else name
        definition_text = f"{title} {body} ({author}, {year})"
        # Decide whether the Daftar Pustaka actually backs this citation.
        if draw(st.booleans()):
            bib = BibliographyResult.from_keys([f"{name}, {year}"])
    else:
        definition_text = f"{title} {body}"

    drafts = [Paragraph(text=definition_text, is_definition=False)]

    # Optionally append a few trailing (non-definition) claim paragraphs.
    extra = draw(st.integers(min_value=0, max_value=3))
    for _ in range(extra):
        drafts.append(Paragraph(text=draw(_plain_sentence()), is_definition=False))

    return entry, drafts, bib


# --------------------------------------------------------------------------- #
# Property 4
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 4: Paragraf definisi bersitasi pada Sub_Bab_Teori
@settings(max_examples=100)
@given(scenario=definition_scenario())
def test_property_4_cited_definition_first_paragraph(scenario) -> None:
    """Property 4: Paragraf definisi bersitasi pada Sub_Bab_Teori.

    Untuk setiap Sub_Bab_Teori yang disusun, paragraf pertama adalah tepat satu
    paragraf definisi konsep utama, dan paragraf tersebut memuat paling sedikit
    satu Sitasi_APA in-text yang menempel -- atau, bila tidak, paragraf pertama
    ditandai dengan Penanda_Sitasi_Kurang.

    Validates: Requirements 2.1, 2.2, 2.4
    """
    entry, drafts, bib = scenario

    block, _findings = write_theory_subchapter(
        entry, facts=None, bib=bib, drafts=drafts
    )

    paragraphs = block.paragraphs
    assert paragraphs, "Sub_Bab_Teori harus memiliki minimal satu paragraf"

    # Requirement 2.1: the first paragraph is a definition AND it is the ONLY
    # definition paragraph of the sub-chapter.
    first = paragraphs[0]
    assert first.is_definition, "paragraf pertama harus paragraf definisi"
    assert sum(1 for p in paragraphs if p.is_definition) == 1, (
        "hanya paragraf pertama yang boleh menjadi paragraf definisi"
    )

    # Requirements 2.2 / 2.4: the definition paragraph either carries a
    # bibliography-backed APA citation, or it is marked [BUTUH SITASI].
    citations = find_citations(first.text)
    has_backed_citation = any(bib.covers(c) for c in citations)
    is_marked = MISSING_CITATION_MARKER in first.text

    assert has_backed_citation or is_marked, (
        "paragraf definisi wajib memuat Sitasi_APA yang didukung Daftar Pustaka "
        "(Req 2.2) atau ditandai [BUTUH SITASI] (Req 2.4)"
    )

    # The two branches are mutually reinforcing with the writer's own predicate:
    # a paragraph with a bibliography-backed citation is a validated cited
    # definition, so it must NOT be forced to carry the missing-citation marker;
    # conversely, an unbacked definition must be marked.
    if has_backed_citation:
        assert has_cited_definition(first), (
            "definisi dengan sitasi harus dikenali sebagai cited definition"
        )
    else:
        assert is_marked, (
            "definisi tanpa sitasi tervalidasi harus ditandai [BUTUH SITASI]"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
