"""Property-based test for the FactVerifier of the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers task 7.2 (Property 12) against the PURE fact-resolution helpers exposed by
``skills/scripts/alur_penulisan/fact_verifier.py``:

  FactStore.from_mapping, resolve_fact, emit_value.

Fact resolution is a pure lookup-before-write transformation over an in-memory
Basis_Fakta view, so 100+ Hypothesis iterations are cheap. This is a brand-new
file; nothing here touches disk (the FactStore is built from a mapping).
"""
import string
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the FactVerifier from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.fact_verifier import (  # noqa: E402
    FactStore,
    emit_value,
    resolve_fact,
)

# --------------------------------------------------------------------------- #
# Strategies: build arbitrary Basis_Fakta mappings with present + absent keys.
# --------------------------------------------------------------------------- #
# Keys are flat identifiers (no dots) so no accidental nested-path resolution.
_KEYS = st.text(alphabet=string.ascii_letters + "_", min_size=1, max_size=8)

# A "present" scalar is any value the FactStore treats as a writable fact:
# a str (that is not the "TBD" sentinel), an int, a finite float, or a bool.
_PRESENT_SCALARS = st.one_of(
    st.text(min_size=0, max_size=20).filter(lambda s: s.strip().lower() != "tbd"),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
)


@st.composite
def fact_scenarios(draw: st.DrawFn):
    """Generate ``(facts, present_keys, absent_keys)``.

    A random set of unique keys is partitioned: some keys are assigned present
    scalar values (stored in ``facts``), the rest are left out of ``facts`` and
    are therefore absent from Basis_Fakta.
    """
    keys = draw(st.lists(_KEYS, unique=True, min_size=1, max_size=6))
    facts: dict[str, object] = {}
    present_keys: list[str] = []
    absent_keys: list[str] = []
    for key in keys:
        if draw(st.booleans()):
            facts[key] = draw(_PRESENT_SCALARS)
            present_keys.append(key)
        else:
            absent_keys.append(key)
    return facts, present_keys, absent_keys


def _differing_candidate(draw: st.DrawFn, avoid: str) -> str:
    """Draw a candidate string guaranteed to differ from ``avoid``."""
    candidate = draw(st.text(max_size=25))
    if candidate == avoid:
        candidate = avoid + "_CANDIDATE_DIFF"
    return candidate


# --------------------------------------------------------------------------- #
# Property 12
# --------------------------------------------------------------------------- #
# Feature: automated-writing-workflow, Property 12: Sumber nilai fakta terbatas pada Basis_Fakta atau Placeholder_TBD
@settings(max_examples=200)
@given(scenario=fact_scenarios(), data=st.data())
def test_property_12_fact_value_source_is_limited(scenario, data) -> None:
    """Property 12: Sumber nilai fakta terbatas pada Basis_Fakta atau Placeholder_TBD.

    Untuk setiap permintaan penulisan nilai fakta/angka proyek: bila nilainya
    tersedia pada Basis_Fakta, nilai yang ditulis sama persis dengan yang
    tercatat (tanpa pembulatan atau penambahan) dan nilai kandidat lain yang
    berbeda ditolak; bila tidak tersedia, yang ditulis adalah Placeholder_TBD
    berisi deskripsi fakta. Tidak ada nilai fakta yang berasal dari sumber
    selain Basis_Fakta atau Placeholder_TBD.

    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
    """
    facts, present_keys, absent_keys = scenario
    store = FactStore.from_mapping(facts)

    # ------------------------------------------------------------------ #
    # Present facts: exact value written, differing candidate rejected.
    # ------------------------------------------------------------------ #
    for key in present_keys:
        recorded = facts[key]

        # Baseline emission without any candidate = the Basis_Fakta value.
        base = emit_value(key, store)

        # resolve_fact reports the fact as present before anything is written
        # (Requirement 5.1: look up before writing).
        fact = resolve_fact(key, store)
        assert fact.present is True
        assert fact.value == base

        # Exactness: the written text represents the recorded value with no
        # rounding, truncation, or additions (Requirement 5.2). Verified by
        # parsing the emitted string back and comparing to the recorded value.
        if isinstance(recorded, bool):
            assert base in ("true", "false")
            assert (base == "true") is recorded
        elif isinstance(recorded, int):
            assert int(base) == recorded
        elif isinstance(recorded, float):
            assert float(base) == recorded
        else:  # str
            assert base == recorded

        # A candidate that differs from Basis_Fakta must be rejected: the
        # emitted value is the Basis_Fakta value, never the foreign candidate
        # (Requirements 5.4, 5.5).
        candidate = _differing_candidate(data.draw, base)
        emitted_with_candidate = emit_value(key, store, candidate=candidate)
        assert emitted_with_candidate == base
        assert emitted_with_candidate != candidate

    # ------------------------------------------------------------------ #
    # Absent facts: Placeholder_TBD with the fact description, candidate ignored.
    # ------------------------------------------------------------------ #
    for key in absent_keys:
        description = f"deskripsi-{key}"
        candidate = data.draw(st.text(max_size=25))

        fact = resolve_fact(key, store, candidate=candidate, description=description)
        assert fact.present is False
        assert fact.value is None

        emitted = emit_value(key, store, candidate=candidate, description=description)

        # Written as a Placeholder_TBD containing the fact description
        # (Requirement 5.3), never the foreign candidate (Requirement 5.5).
        assert emitted.startswith("[TBD:")
        assert emitted.endswith("]")
        assert description in emitted
        assert emitted != candidate

        # Source-limited: the emitted text is a Placeholder_TBD and is NOT any
        # recorded Basis_Fakta value (Requirement 5.5).
        assert emitted not in {str(v) for v in facts.values()}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
