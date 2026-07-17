"""Property-based test for TermConsistencyChecker inconsistency reporting.

Spec: .kiro/specs/automated-writing-workflow

Covers task 10.3 (Property 15) against the PURE reporting helper exposed by
``skills/scripts/alur_penulisan/term_checker.py``:

    scan_terms(draft, registry) -> list[InconsistencyReport]

A draft is built to contain two or more *distinct* surface forms of the SAME
concept (all mapping to the same registered canonical form — e.g. ``navmesh``
vs ``NAVMESH`` vs ``Nav``). The property asserts two things (Requirement 6.3):

  1. The report produced for that concept lists EVERY surface form found,
     together with its 1-based line location.
  2. The draft is NOT modified automatically — the serialized draft after the
     scan is byte-for-byte identical to the draft before the scan.

``scan_terms`` is a pure text scan over an in-memory DraftModel, so 100+
Hypothesis iterations are cheap. Nothing here touches disk. This is a brand-new
file.
"""
import string
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the TermConsistencyChecker from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.models import TermRegistry  # noqa: E402
from alur_penulisan.term_checker import scan_terms  # noqa: E402

# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #
_WORD = st.text(alphabet=string.ascii_lowercase, min_size=3, max_size=8)
# Case transforms produce differing surface forms of the same word. For a
# lowercase base of length >= 3 these are guaranteed distinct from each other.
_CASE_FNS = [str.lower, str.upper, str.capitalize]


@st.composite
def inconsistent_term_drafts(draw: st.DrawFn):
    """Build ``(text, registry, expected, canonical)``.

    ``text`` is a Markdown draft embedding two or more distinct surface forms of
    a single registered concept. ``expected`` is the list of ``(form, line_no)``
    occurrences that ``scan_terms`` SHOULD report, in document order.
    """
    base = draw(_WORD)  # lowercase concept word (a registered variant)

    # Optionally register a distinct synonym word for the SAME concept. It must
    # be unrelated to ``base`` (neither a substring of the other) so the two
    # variant matchers never overlap on a single occurrence.
    use_syn = draw(st.booleans())
    synonym = None
    if use_syn:
        synonym = draw(
            _WORD.filter(lambda w: w != base and base not in w and w not in base)
        )

    canonical = base.capitalize()  # canonical surface form for the concept
    registry_map = {base: canonical}
    variant_bases = [base]
    if synonym is not None:
        registry_map[synonym] = canonical
        variant_bases.append(synonym)
    registry = TermRegistry(canonical=registry_map)

    # Generate the surface occurrences (each a case-variant of a variant base).
    n_occ = draw(st.integers(min_value=2, max_value=8))
    occurrences: list[str] = []
    for _ in range(n_occ):
        vb = draw(st.sampled_from(variant_bases))
        cf = draw(st.sampled_from(_CASE_FNS))
        occurrences.append(cf(vb))

    # Requirement 6.3 precondition: at least two DISTINCT surface forms must be
    # present. Force it deterministically if the random draw collapsed them.
    if len(set(occurrences)) < 2:
        occurrences[0] = base
        occurrences[1] = base.upper()

    # Filler words that never collide with a registered variant (whole-word,
    # case-insensitive). Substrings are safe because the matcher uses word
    # boundaries, so equality filtering is sufficient.
    forbidden = {vb for vb in variant_bases}
    filler_word = _WORD.filter(lambda w: w not in forbidden)

    lines: list[str] = []
    expected: list[tuple[str, int]] = []

    for surface in occurrences:
        # Occasionally emit a pure-filler line (no term) before the occurrence
        # to exercise line-number tracking across non-matching lines.
        if draw(st.booleans()):
            filler = draw(st.lists(filler_word, min_size=1, max_size=4))
            lines.append(" ".join(filler))

        # Place the term mid-line (never at line start) surrounded by filler so
        # the surface form appears exactly once on this line.
        prefix = draw(st.lists(filler_word, min_size=1, max_size=3))
        suffix = draw(st.lists(filler_word, min_size=0, max_size=3))
        line = " ".join([*prefix, surface, *suffix])
        lines.append(line)
        expected.append((surface, len(lines)))  # 1-based line number

    # Optional trailing filler line.
    if draw(st.booleans()):
        filler = draw(st.lists(filler_word, min_size=1, max_size=4))
        lines.append(" ".join(filler))

    text = "\n".join(lines)
    return text, registry, expected, canonical


# --------------------------------------------------------------------------- #
# Property 15
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 15: Laporan inkonsistensi istilah tanpa mutasi otomatis
@settings(max_examples=100, deadline=None)
@given(scenario=inconsistent_term_drafts())
def test_property_15_inconsistency_report_without_automatic_mutation(scenario) -> None:
    """Property 15: Laporan inkonsistensi istilah tanpa mutasi otomatis.

    Untuk setiap Berkas_Draf yang memuat dua atau lebih bentuk berbeda untuk
    satu konsep yang sama (padanan baku terdaftar sama), laporan yang dihasilkan
    memuat setiap bentuk yang ditemukan beserta lokasi kemunculannya, dan isi
    Berkas_Draf tidak diubah secara otomatis (draf keluaran identik dengan draf
    masukan).

    Validates: Requirements 6.3
    """
    text, registry, expected, canonical = scenario
    draft = DraftModel.from_markdown(text)

    # Snapshot the serialized draft BEFORE scanning to detect any mutation.
    before = draft.to_markdown()

    reports = scan_terms(draft, registry)

    # --- No automatic mutation: the draft is unchanged by the scan. --------- #
    after = draft.to_markdown()
    assert after == before

    # --- Exactly one concept was registered, and it is reported (2+ forms). -- #
    matching = [r for r in reports if r.concept_key == canonical]
    assert len(matching) == 1, (
        f"expected exactly one inconsistency report for concept "
        f"{canonical!r}, got {[r.concept_key for r in reports]}"
    )
    report = matching[0]

    # The precondition (two or more differing forms) actually holds.
    reported_forms = {occ.form for occ in report.forms}
    assert len(reported_forms) >= 2

    # --- Every placed occurrence is reported with its exact form + location. - #
    actual = sorted((occ.form, occ.line) for occ in report.forms)
    assert actual == sorted(expected)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
