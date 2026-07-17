"""Property test for the end-to-end idempotency of ``run_alur`` (R1.4, R8.1) of
the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 3: Idempotensi menjalankan ulang alur** — for every
Berkas_Draf, running the flow twice yields a chapter / sub-chapter structure
(titles, order, numbering) identical to running it once; no duplicate chapter or
sub-chapter is ever added.

The orchestration (``run_alur``) performs I/O only through the injected
``read`` / ``write`` / ``load_facts`` hooks, so this test wires them to a small
in-memory closure holding the draft text as state: run 1's *written* output is
fed straight into run 2. ``active_branch="laporan/iman"`` keeps the Peran_Branch
resolved so both runs complete (no HELD/FAILED short-circuit).
"""
import sys
from collections import Counter
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.fact_verifier import FactStore  # noqa: E402
from alur_penulisan.pipeline import RunStatus, run_alur  # noqa: E402
from alur_penulisan.skeleton import canonical_skeleton, entry_heading_text  # noqa: E402

_ENTRIES = canonical_skeleton().entries

# Body text alphabet free of Markdown control characters (no '#', '|', '-',
# '[', ']', '`', '*', '+') so generated paragraphs never masquerade as headings,
# list items, tables or page breaks.
_SAFE_TEXT = "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "


@st.composite
def _vary_case(draw, text: str) -> str:
    """Randomly upper/lower/leave each character (heading matching ignores case)."""
    return "".join(draw(st.sampled_from([ch, ch.upper(), ch.lower()])) for ch in text)


@st.composite
def _initial_draft(draw):
    """Build an arbitrary initial Berkas_Draf (empty, partial, or fuller).

    A random subset of canonical entries is emitted *in canonical order* with
    case/edge-whitespace-varied headings and optional free-form body paragraphs
    (standing in for Konten_Manual). An optional preamble paragraph exercises the
    front-matter path. The empty-draft edge case is included when the subset and
    preamble are both empty.
    """
    lines: list[str] = []

    # Optional preamble (front matter before the first BAB heading).
    if draw(st.booleans()):
        lines.append(draw(st.text(alphabet=_SAFE_TEXT, min_size=0, max_size=40)))
        lines.append("")

    included = draw(
        st.lists(
            st.integers(min_value=0, max_value=len(_ENTRIES) - 1),
            unique=True,
        )
    )
    for idx in sorted(included):
        entry = _ENTRIES[idx]
        base = entry_heading_text(entry)
        varied = draw(_vary_case(base))
        lead = " " * draw(st.integers(min_value=0, max_value=2))
        trail = " " * draw(st.integers(min_value=0, max_value=2))
        prefix = "#" * entry.level.value
        lines.append(f"{prefix} {lead}{varied}{trail}")
        lines.append("")
        if draw(st.booleans()):
            body = draw(st.text(alphabet=_SAFE_TEXT, min_size=1, max_size=50)).strip()
            if body:
                lines.append(body)
                lines.append("")

    return "\n".join(lines)


def _heading_structure(markdown: str):
    """Ordered ``(level, normalized-text)`` for every heading in ``markdown``.

    Captures titles, order and hierarchical numbering (the numbering is part of
    the heading text) at the depth encoded by the heading level.
    """
    model = DraftModel.from_markdown(markdown)
    return [
        (h.meta.get("level", 0), str(h.meta.get("text", "")).strip())
        for h in model.headings()
    ]


def _make_hooks(initial_text: str):
    """In-memory I/O hooks: a shared cell whose written value feeds the next read."""
    state = {"text": initial_text}

    def read(_path: str) -> str:
        return state["text"]

    def write(_path: str, content: str) -> None:
        state["text"] = content

    def load_facts(_path=None, *args, **kwargs):
        # Keep facts fully in-memory (empty, accessible) — no disk access.
        return FactStore.from_mapping({})

    return state, read, write, load_facts


# =========================================================================== #
# Property 3: Idempotensi menjalankan ulang alur
# =========================================================================== #
# Feature: automated-writing-workflow, Property 3: Idempotensi menjalankan ulang alur
# Validates: Requirements 1.4, 8.1
@settings(max_examples=100, deadline=None)
@given(initial=_initial_draft())
def test_rerunning_flow_is_idempotent(initial):
    state, read, write, load_facts = _make_hooks(initial)

    # --- Run once -------------------------------------------------------- #
    r1 = run_alur(
        active_branch="laporan/iman",
        read=read,
        write=write,
        load_facts=load_facts,
    )
    assert r1.status is RunStatus.COMPLETED, f"first run did not complete: {r1.status}"
    once = state["text"]  # written output of run 1

    # --- Run twice (feed run 1's output into run 2) ---------------------- #
    r2 = run_alur(
        active_branch="laporan/iman",
        read=read,
        write=write,
        load_facts=load_facts,
    )
    assert r2.status is RunStatus.COMPLETED, f"second run did not complete: {r2.status}"
    twice = state["text"]  # written output of run 2 (read run 1's output)

    struct_once = _heading_structure(once)
    struct_twice = _heading_structure(twice)

    # Structure (titles, order, numbering, depth) after a re-run is identical to
    # after a single run.
    assert struct_twice == struct_once, (
        "heading structure changed on re-run (not idempotent):\n"
        f"  once={struct_once}\n  twice={struct_twice}"
    )

    # No duplicate chapter / sub-chapter was added: every heading key appears
    # exactly once in the re-run output.
    counts = Counter(struct_twice)
    dupes = {key: n for key, n in counts.items() if n > 1}
    assert not dupes, f"duplicate headings introduced on re-run: {dupes}"
