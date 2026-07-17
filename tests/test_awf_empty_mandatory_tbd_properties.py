"""Property test for empty mandatory sections receiving a Placeholder_TBD (R10.4)
of the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 26: Bagian wajib kosong diberi Placeholder_TBD** —
"Untuk setiap bagian wajib yang kosong pada Berkas_Draf yang dapat diakses, alur
menuliskan Placeholder_TBD pada bagian wajib tersebut."

For any accessible draft that contains a random subset of the canonical mandatory
(leaf) sections — some with empty bodies, some with real content —
``fill_empty_mandatory_sections`` must insert a ``[TBD: ...]`` marker into every
empty mandatory section and leave the non-empty ones untouched.

``fill_empty_mandatory_sections`` is a pure transform, so 100+ Hypothesis
iterations are cheap.
"""
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the alur_penulisan package (pure core under skills/scripts).
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.draft_model import DraftModel  # noqa: E402
from alur_penulisan.report import (  # noqa: E402
    TBD_MARKER_RE,
    fill_empty_mandatory_sections,
    find_empty_mandatory_sections,
    mandatory_sections,
)
from alur_penulisan.skeleton import entry_heading_markdown  # noqa: E402

# The canonical mandatory (leaf) sections — the "bagian wajib" that must carry
# prose. Computed once; the property builds drafts from random subsets of these.
_MANDATORY = mandatory_sections()


def _count_tbd_markers(draft: DraftModel) -> int:
    """Number of Placeholder_TBD (``[TBD: ...]``) markers across all blocks."""
    return sum(
        len(TBD_MARKER_RE.findall("\n".join(block.lines))) for block in draft.blocks
    )


@st.composite
def _draft_with_mandatory_sections(draw):
    """Build a draft holding a random subset of mandatory sections.

    Each canonical mandatory (leaf) entry is independently either:

    * ``"absent"`` — not present in the draft at all,
    * ``"empty"``  — present as a heading with a blank body (a *bagian wajib
      kosong* that must receive a Placeholder_TBD), or
    * ``"filled"`` — present as a heading followed by a unique paragraph of real
      content (must be left untouched).

    Returns ``(draft, empty_entries, filled_texts)`` where ``empty_entries`` are
    the entries with empty bodies and ``filled_texts`` maps each filled entry_id
    to the unique content string written under its heading.
    """
    states = draw(
        st.lists(
            st.sampled_from(["absent", "empty", "filled"]),
            min_size=len(_MANDATORY),
            max_size=len(_MANDATORY),
        )
    )

    lines: list[str] = []
    empty_entries = []
    filled_texts: dict[str, str] = {}

    for entry, state in zip(_MANDATORY, states):
        if state == "absent":
            continue
        lines.append(entry_heading_markdown(entry))
        lines.append("")
        if state == "empty":
            empty_entries.append(entry)
        else:  # filled
            content = f"Konten nyata untuk bagian {entry.entry_id}."
            filled_texts[entry.entry_id] = content
            lines.append(content)
            lines.append("")

    draft = DraftModel.from_markdown("\n".join(lines))
    return draft, empty_entries, filled_texts


# =========================================================================== #
# Property 26: Bagian wajib kosong diberi Placeholder_TBD
# =========================================================================== #
# Feature: automated-writing-workflow, Property 26: Bagian wajib kosong diberi Placeholder_TBD
# Validates: Requirements 10.4
@settings(max_examples=200, deadline=None)
@given(data=_draft_with_mandatory_sections())
def test_empty_mandatory_sections_get_tbd_placeholder(data):
    draft, empty_entries, filled_texts = data

    # Sanity: the generated draft indeed exposes exactly the intended empties.
    detected = find_empty_mandatory_sections(draft)
    assert len(detected) == len(empty_entries), (
        f"setup mismatch: detected {len(detected)} empty sections, "
        f"expected {len(empty_entries)}"
    )

    new_draft, findings = fill_empty_mandatory_sections(draft)

    # One Placeholder_TBD finding per empty mandatory section.
    assert len(findings) == len(empty_entries), (
        f"expected {len(empty_entries)} findings, got {len(findings)}"
    )

    # Exactly one [TBD: ...] marker was written per empty section — no more, no
    # fewer. Equal totals with a filled-untouched count of zero means every empty
    # section received exactly one marker and no filled section received any.
    assert _count_tbd_markers(new_draft) == len(empty_entries), (
        f"expected {len(empty_entries)} TBD markers, "
        f"got {_count_tbd_markers(new_draft)}"
    )

    # After filling, no mandatory section remains empty.
    assert find_empty_mandatory_sections(new_draft) == [], (
        "a mandatory section is still empty after fill"
    )

    # Non-empty (filled) sections are left untouched: their original content
    # survives verbatim in the resulting draft.
    rendered = new_draft.to_markdown()
    for content in filled_texts.values():
        assert content in rendered, f"filled content lost: {content!r}"
