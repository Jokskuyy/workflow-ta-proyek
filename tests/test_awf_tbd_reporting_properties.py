"""Property-based test for ReportBuilder Placeholder_TBD reporting.

Spec: .kiro/specs/automated-writing-workflow

Covers task 14.3 (Property 27) against the PURE reporting helpers exposed by
``skills/scripts/alur_penulisan/report.py``:

    collect_tbd_findings(draft) -> list[Finding]
    build_report(findings, draft=..., active_role=...) -> WriterReport

Requirement 10.5 / Property 27: for every Placeholder_TBD (``[TBD: <cause>]``)
that the workflow writes into a draft, the writer report contains one entry for
that section together with its cause — so the number of TBD report entries
equals the number of Placeholder_TBD markers in the draft (count parity), and
each entry carries the marker's cause.

The strategy builds a Markdown draft embedding a random number of
``[TBD: <reason>]`` markers (with reasons drawn from a bracket-free alphabet so
no accidental / nested markers are produced), one per paragraph, interleaved
with filler paragraphs that contain no markers. The property then asserts:

  1. ``collect_tbd_findings`` returns exactly one ``Finding(TBD)`` per marker
     (count parity), in reading order.
  2. Each finding carries the marker's cause (detail derived from the reason).
  3. ``build_report(draft=...)`` reports a TBD count equal to the number of
     markers in the draft.

Everything is a pure in-memory scan, so 100+ Hypothesis iterations are cheap
and nothing touches disk. This is a brand-new file.
"""
import string
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the ReportBuilder helpers from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.models import FindingKind  # noqa: E402
from alur_penulisan.report import (  # noqa: E402
    build_report,
    collect_tbd_findings,
    make_tbd_marker,
)

# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #
# Bracket-free words: no '[' or ']' so filler / reasons can never form (or break)
# a Placeholder_TBD marker. Lowercase letters keep reasons non-empty and stable
# under the marker grammar's whitespace stripping.
_WORD = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=8)


def _expected_detail(reason: str) -> str:
    """Mirror report.collect_tbd_findings' detail construction for a cause."""
    reason = reason.strip()
    return (
        f"Placeholder_TBD: {reason}"
        if reason
        else "Placeholder_TBD tanpa deskripsi."
    )


@st.composite
def tbd_drafts(draw: st.DrawFn):
    """Build ``(text, expected_details)``.

    ``text`` is a Markdown draft embedding ``len(expected_details)`` markers
    ``[TBD: <reason>]`` (one per paragraph), interleaved with marker-free filler
    paragraphs. ``expected_details`` is the ordered list of finding detail
    strings that the collector SHOULD produce, in reading order.
    """
    # Reasons are non-empty phrases of 1..4 bracket-free words joined by single
    # spaces, so each reason survives whitespace-stripping as a distinct cause.
    reason_strategy = st.lists(_WORD, min_size=1, max_size=4).map(" ".join)

    reasons = draw(st.lists(reason_strategy, min_size=0, max_size=8))

    # Marker-free filler paragraph (bracket-free words only).
    filler_para = st.lists(_WORD, min_size=1, max_size=5).map(" ".join)

    lines: list[str] = []
    expected: list[str] = []

    for reason in reasons:
        # Optionally emit a marker-free filler paragraph before the marker to
        # exercise ordering across non-matching blocks.
        if draw(st.booleans()):
            lines.append(draw(filler_para))
            lines.append("")  # blank line separates paragraphs

        lines.append(make_tbd_marker(reason))
        lines.append("")  # blank line separates paragraphs
        expected.append(_expected_detail(reason))

    # Optional trailing filler paragraph.
    if draw(st.booleans()):
        lines.append(draw(filler_para))

    text = "\n".join(lines)
    return text, expected


# --------------------------------------------------------------------------- #
# Property 27
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 27: Setiap Placeholder_TBD dilaporkan beserta penyebabnya
@settings(max_examples=100, deadline=None)
@given(scenario=tbd_drafts())
def test_property_27_every_tbd_reported_with_cause(scenario) -> None:
    """Property 27: Setiap Placeholder_TBD dilaporkan beserta penyebabnya.

    Untuk setiap Placeholder_TBD yang dituliskan alur, laporan kepada penulis
    memuat entri bagian tersebut beserta penyebabnya (jumlah entri laporan TBD
    sama dengan jumlah Placeholder_TBD pada draf).

    Validates: Requirements 10.5
    """
    text, expected = scenario
    draft = DraftModel.from_markdown(text)

    # --- collect_tbd_findings: one Finding(TBD) per marker, in reading order. #
    findings = collect_tbd_findings(draft)

    # Every finding is a TBD finding.
    assert all(f.kind is FindingKind.TBD for f in findings)

    # Count parity: exactly one entry per Placeholder_TBD marker.
    assert len(findings) == len(expected)

    # Each finding carries the marker's cause (in reading order).
    assert [f.detail for f in findings] == expected

    # --- build_report(draft=...): TBD entry count equals number of markers. -- #
    report = build_report([], draft=draft, active_role="iman")
    tbd_entries = [f for f in report.findings if f.kind is FindingKind.TBD]
    assert len(tbd_entries) == len(expected)
    assert [f.detail for f in tbd_entries] == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
