"""Property-based test for baku-term consistency (automated-writing-workflow).

Spec: .kiro/specs/automated-writing-workflow

Covers task 10.2 (Property 14) against the PURE TermConsistencyChecker exposed
by ``skills/scripts/alur_penulisan/term_checker.py``:

  canonical_form(term, registry) -> str | None
  resolve_form(term, registry, first_seen) -> str

Property 14 — Konsistensi istilah berpadanan baku (Requirements 6.1, 6.2):

  For every term that has a registered baku (canonical) form, EVERY occurrence
  — regardless of the letter case it was written in — is normalized to one
  single, identical canonical form throughout the draft. Matching ignores
  letter-case differences.

This is verified by driving both writer-side normalization (``resolve_form``)
and the lookup (``canonical_form``) with case-varied surface forms of the same
registered term and asserting they all collapse to the one canonical string.

Nothing here touches disk; the registry and surface forms are built in memory,
so 100+ Hypothesis iterations are cheap.
"""
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

from alur_penulisan.models import TermRegistry  # noqa: E402
from alur_penulisan.term_checker import canonical_form, resolve_form  # noqa: E402

# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #
# A term token: letters (mixed case allowed in the canonical form), digits, and
# internal single spaces so multi-word terms like "nav mesh" are covered. We
# keep the token non-empty and free of leading/trailing whitespace so it is a
# well-formed registry entry.
_TERM_WORD = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    min_size=1,
    max_size=8,
)


@st.composite
def registry_and_terms(draw: st.DrawFn):
    """Generate ``(registry, canonical_by_key)``.

    ``registry`` is a :class:`TermRegistry` mapping a *lower-cased* variant key
    to its canonical (baku) surface form, exactly as the design prescribes
    (``{"navmesh": "NavMesh"}``). ``canonical_by_key`` echoes that mapping for
    the assertions.

    Canonical forms are guaranteed distinct after normalization so that each
    generated term is an independent concept.
    """
    words = draw(
        st.lists(_TERM_WORD, min_size=1, max_size=6, unique_by=lambda w: w.lower())
    )
    canonical_by_key: dict[str, str] = {}
    for word in words:
        # The canonical form is the (arbitrarily-cased) word; its key is lower.
        canonical_by_key[word.lower()] = word
    registry = TermRegistry(canonical=dict(canonical_by_key))
    return registry, canonical_by_key


def _case_variants(draw: st.DrawFn, form: str) -> list[str]:
    """Produce several case-varied spellings of ``form`` (same letters)."""
    variants = {form, form.lower(), form.upper()}
    # A random per-character case flip to broaden coverage.
    flipped = "".join(
        (ch.upper() if draw(st.booleans()) else ch.lower()) for ch in form
    )
    variants.add(flipped)
    # Title-ish variant.
    variants.add(form.swapcase())
    return list(variants)


# --------------------------------------------------------------------------- #
# Property 14
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 14: Konsistensi istilah berpadanan baku
@settings(max_examples=150)
@given(data=st.data(), scenario=registry_and_terms())
def test_property_14_registered_terms_normalize_to_single_baku_form(data, scenario) -> None:
    """Property 14: Konsistensi istilah berpadanan baku.

    Untuk setiap istilah yang memiliki padanan baku terdaftar, seluruh
    kemunculannya dinormalkan ke satu bentuk baku yang identik di seluruh
    Berkas_Draf, dengan pencocokan yang mengabaikan perbedaan huruf besar/kecil.

    Validates: Requirements 6.1, 6.2
    """
    registry, canonical_by_key = scenario

    for key, canonical in canonical_by_key.items():
        # Every case-varied spelling of this registered term...
        surface_forms = _case_variants(data.draw, canonical)

        # A fresh first-seen map per draft run (registered terms never consult
        # it, but resolve_form requires the argument).
        first_seen: dict[str, str] = {}

        resolved_set = set()
        for surface in surface_forms:
            # (6.2) case-insensitive lookup returns the registered canonical form.
            assert canonical_form(surface, registry) == canonical, (
                f"canonical_form({surface!r}) should be {canonical!r}"
            )

            # (6.1) writer-side normalization uses that single baku form.
            resolved = resolve_form(surface, registry, first_seen)
            assert resolved == canonical, (
                f"resolve_form({surface!r}) should be {canonical!r}, got {resolved!r}"
            )
            resolved_set.add(resolved)

        # (6.1) all occurrences collapse to exactly ONE identical form.
        assert resolved_set == {canonical}, (
            f"expected single baku form {canonical!r}, got {resolved_set!r}"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
