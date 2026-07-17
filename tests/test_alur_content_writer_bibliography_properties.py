"""Property-based test for SectionContentWriter citation/bibliography validation.

Spec: .kiro/specs/automated-writing-workflow

Covers task 6.4 (Property 6) against the PURE SectionContentWriter helpers exposed by
``skills/scripts/alur_penulisan/content_writer.py``:

  find_citations, mark_paragraph_citations, BibliographyResult, MISSING_CITATION_MARKER.

Citation validation is a pure text-in/text-out transformation, so 100+ Hypothesis
iterations are cheap. The existing pipeline test suites are NOT modified; this is a
brand-new file. Nothing here touches disk.
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
    MISSING_CITATION_MARKER,
    BibliographyResult,
    find_citations,
    mark_paragraph_citations,
)
from alur_penulisan.models import FindingKind, Paragraph  # noqa: E402


# --------------------------------------------------------------------------- #
# Strategies: build APA citations, each either backed by a Daftar Pustaka entry
# or not, then weave them into a single non-definition paragraph.
# --------------------------------------------------------------------------- #
# Author surnames: ascii letters only so they never contain ';', '(', ')', ','
# or a 4-digit year that could confuse the APA citation grammar.
_SURNAME = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    min_size=3,
    max_size=10,
)
_YEAR = st.integers(min_value=1900, max_value=2099).map(str)


@st.composite
def cited_paragraphs(draw: st.DrawFn):
    """Return ``(paragraph, bibliography, sources)``.

    ``sources`` is a list of ``(name, year, covered)`` triples; each triple
    becomes one single-source APA citation ``(name, year)`` embedded in the
    paragraph. ``covered`` marks whether the source has a matching Daftar Pustaka
    entry. Surnames are unique so every citation is distinct and locatable.
    """
    # Unique surnames keep each citation's comparison key distinct.
    names = draw(
        st.lists(_SURNAME, min_size=1, max_size=5, unique_by=lambda s: s.casefold())
    )
    sources = []
    for name in names:
        year = draw(_YEAR)
        covered = draw(st.booleans())
        sources.append((name, year, covered))

    # Build the Daftar Pustaka from only the covered sources.
    bib = BibliographyResult.from_keys(
        [f"{name}, {year}" for name, year, covered in sources if covered]
    )

    # Weave each citation into its own sentence; no parentheses/years elsewhere.
    sentences = [
        f"Pernyataan faktual bagian ini menjelaskan sesuatu ({name}, {year})"
        for name, year, _covered in sources
    ]
    text = ". ".join(sentences) + "."
    return Paragraph(text=text, is_definition=False), bib, sources


def _marker_follows_citation(output: str, raw: str) -> bool:
    """True when every occurrence of citation ``raw`` in ``output`` is directly
    followed (ignoring surrounding whitespace) by the Penanda_Sitasi_Kurang."""
    start = 0
    found_any = False
    while True:
        idx = output.find(raw, start)
        if idx == -1:
            break
        found_any = True
        tail = output[idx + len(raw):].lstrip()
        if not tail.startswith(MISSING_CITATION_MARKER):
            return False
        start = idx + len(raw)
    return found_any


# --------------------------------------------------------------------------- #
# Property 6
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 6: Sitasi tanpa entri Daftar Pustaka ditandai
@settings(max_examples=100)
@given(data=cited_paragraphs())
def test_property_6_citation_without_bibliography_entry_is_marked(data) -> None:
    """Property 6: Sitasi tanpa entri Daftar Pustaka ditandai.

    Untuk setiap Sitasi_APA yang tidak memiliki entri padanan pada Daftar
    Pustaka, sitasi tersebut ditandai dengan Penanda_Sitasi_Kurang dan klaim
    terkaitnya tidak diperlakukan sebagai klaim yang sudah tervalidasi.

    Validates: Requirements 2.5
    """
    paragraph, bib, sources = data
    result, findings = mark_paragraph_citations(paragraph, bib, location="2.1 ¶1")

    uncovered = [(name, year) for name, year, covered in sources if not covered]

    for name, year in uncovered:
        raw = f"({name}, {year})"

        # The citation is NOT treated as validated: bibliography coverage fails.
        matching = [c for c in find_citations(paragraph.text) if c.raw == raw]
        assert matching, f"citation {raw!r} should be parseable"
        assert not any(bib.covers(c) for c in matching), (
            f"citation {raw!r} has no Daftar Pustaka entry so it must not be covered"
        )

        # The citation is marked with Penanda_Sitasi_Kurang in the output.
        assert _marker_follows_citation(result.text, raw), (
            f"citation {raw!r} without a matching entry must be followed by "
            f"{MISSING_CITATION_MARKER!r}"
        )

        # No text is deleted: the original citation text survives in the output.
        assert raw in result.text

    # Every uncovered citation is reported as a MISSING_CITATION finding.
    missing_findings = [f for f in findings if f.kind == FindingKind.MISSING_CITATION]
    citation_findings = [
        f for f in missing_findings if "Daftar" in f.detail
    ]
    assert len(citation_findings) == len(uncovered), (
        f"expected {len(uncovered)} missing-entry findings, got {len(citation_findings)}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
