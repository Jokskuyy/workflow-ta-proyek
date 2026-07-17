"""Property-based test for unregistered-term first-occurrence rule.

Spec: .kiro/specs/automated-writing-workflow

Covers task 10.4 (Property 16) against the PURE TermConsistencyChecker exposed
by ``skills/scripts/alur_penulisan/term_checker.py``:

  resolve_form(term, registry, first_seen) -> str

# Feature: automated-writing-workflow, Property 16: Istilah tanpa padanan baku memakai bentuk kemunculan pertama

Property 16 — Validates: Requirements 6.4

For any term that is NOT in the TermRegistry, the surface form seen on its first
occurrence becomes the reference form and is preserved (returned identically)
for every subsequent occurrence within the same draft run. Case-varied later
occurrences of the same term (same normalized key) all resolve back to that
first-seen form.

The transformation is pure and touches no disk, so 100+ Hypothesis iterations
are cheap. This is a brand-new file.
"""
import string
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the TermConsistencyChecker from the alur_penulisan package.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.models import TermRegistry  # noqa: E402
from alur_penulisan.term_checker import resolve_form, _normalize_key  # noqa: E402


# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #
def _case_variants(word: str):
    """Return a strategy producing case-varied renderings of ``word``."""
    return st.builds(
        lambda flags: "".join(
            ch.upper() if flag else ch.lower()
            for ch, flag in zip(word, flags)
        ),
        st.lists(st.booleans(), min_size=len(word), max_size=len(word)),
    )


# A base term made of letters (possibly multi-word with spaces) that will never
# be registered. Kept simple so its normalized key is stable.
_BASE_TERM = st.lists(
    st.text(alphabet=string.ascii_lowercase, min_size=2, max_size=8),
    min_size=1,
    max_size=3,
).map(lambda parts: " ".join(parts))


@st.composite
def _term_and_occurrences(draw):
    """A base term plus a sequence of case-varied occurrences of it."""
    base = draw(_BASE_TERM)
    n = draw(st.integers(min_value=1, max_value=8))
    occurrences = [draw(_case_variants(base)) for _ in range(n)]
    return base, occurrences


# --------------------------------------------------------------------------- #
# Property 16
# --------------------------------------------------------------------------- #
@settings(max_examples=200)
@given(term_and_occurrences=_term_and_occurrences())
def test_unregistered_term_keeps_first_occurrence_form(term_and_occurrences):
    """Validates: Requirements 6.4

    An unregistered term's first-occurrence surface form is the reference and is
    preserved for all subsequent occurrences within the same draft run.
    """
    base, occurrences = term_and_occurrences

    # Empty registry => the term is guaranteed unregistered.
    registry = TermRegistry(canonical={})
    first_seen: dict[str, str] = {}

    resolved = [resolve_form(occ, registry, first_seen) for occ in occurrences]

    first_form = occurrences[0]

    # The first occurrence resolves to itself (its own surface form).
    assert resolved[0] == first_form

    # Every subsequent occurrence (same normalized key) resolves to the
    # first-seen form, regardless of its own casing.
    for occ, res in zip(occurrences, resolved):
        assert _normalize_key(occ) == _normalize_key(base)
        assert res == first_form


@settings(max_examples=200)
@given(
    term_and_occurrences=_term_and_occurrences(),
    registered=st.lists(
        st.tuples(
            st.text(alphabet=string.ascii_lowercase, min_size=2, max_size=6),
            st.text(alphabet=string.ascii_letters, min_size=2, max_size=6),
        ),
        max_size=5,
    ),
)
def test_first_occurrence_stable_with_unrelated_registry(
    term_and_occurrences, registered
):
    """Validates: Requirements 6.4

    Presence of unrelated registered terms does not affect the first-occurrence
    rule for an unregistered term.
    """
    base, occurrences = term_and_occurrences

    base_key = _normalize_key(base)
    # Keep only registry entries that do NOT collide with our base term key,
    # so the base term stays unregistered.
    canonical = {
        k: v for k, v in registered if _normalize_key(k) != base_key
    }
    registry = TermRegistry(canonical=canonical)
    first_seen: dict[str, str] = {}

    resolved = [resolve_form(occ, registry, first_seen) for occ in occurrences]

    first_form = occurrences[0]
    for res in resolved:
        assert res == first_form
