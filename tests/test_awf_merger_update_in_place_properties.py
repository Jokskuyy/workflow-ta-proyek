"""Property test for the IdempotentMerger's in-place chapter update (R8.3) of
the automated-writing-workflow spec.

Spec: .kiro/specs/automated-writing-workflow

Covers design **Property 22: Pembaruan bab yang ada tanpa duplikasi lokasi** —
for every chapter / sub-chapter of the current Kerangka_Bab that already exists
in Berkas_Draf, ``merge`` updates its content *at the same location* so the
chapter still appears exactly once (no duplicate copy of the chapter is
created).

``merge`` is a pure transform (design.md §8 "IdempotentMerger"), so 100+
Hypothesis iterations are cheap.
"""
import sys
from collections import Counter
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
from alur_penulisan.merger import merge  # noqa: E402


# --------------------------------------------------------------------------- #
# Generators
# --------------------------------------------------------------------------- #
_TITLE_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


@st.composite
def _vary_case(draw, text: str) -> str:
    """Return ``text`` with each character randomly upper/lower/unchanged.

    Location matching in the merger is case-insensitive (heading key uses
    ``casefold``), so a case-varied title in the generated draft must still be
    recognised as the *same* chapter and updated in place, not duplicated.
    """
    return "".join(draw(st.sampled_from([ch, ch.upper(), ch.lower()])) for ch in text)


@st.composite
def _scenario(draw):
    """Build an (existing, generated) draft pair sharing some chapter headings.

    Returns a tuple ``(existing_md, generated_md, shared, existing_only,
    generated_only)`` where each of the three lists holds
    ``(level, base_title, idx)`` triples. Bodies are tagged with unique markers
    ``LAMA_{idx}`` (old/existing) and ``BARU_{idx}`` (new/generated) so the test
    can verify shared chapters are updated in place (new body wins, old body
    superseded) while remaining a single copy.
    """
    # Distinct chapter titles (unique ignoring case, non-empty, no markup chars).
    titles = draw(
        st.lists(
            st.text(alphabet=_TITLE_ALPHABET, min_size=3, max_size=8),
            min_size=1,
            max_size=6,
            unique_by=lambda t: t.casefold(),
        )
    )

    chapters = []  # (level, base_title, idx, category)
    saw_shared = False
    for idx, title in enumerate(titles):
        level = draw(st.sampled_from([1, 2]))
        category = draw(st.sampled_from(["shared", "existing_only", "generated_only"]))
        if category == "shared":
            saw_shared = True
        chapters.append((level, title, idx, category))

    # Guarantee the property is exercised: at least one shared chapter.
    if not saw_shared:
        lvl, ttl, idx, _ = chapters[0]
        chapters[0] = (lvl, ttl, idx, "shared")

    shared, existing_only, generated_only = [], [], []
    existing_lines: list[str] = []
    generated_lines: list[str] = []

    for level, title, idx, category in chapters:
        prefix = "#" * level
        if category in ("shared", "existing_only"):
            existing_lines.append(f"{prefix} {title}")
            existing_lines.append("")
            existing_lines.append(f"Isi lama LAMA_{idx} bab ini.")
            existing_lines.append("")
        if category in ("shared", "generated_only"):
            # In the generated draft, shared chapters may carry a case-varied
            # title (same location key); generated-only keep their title.
            gen_title = draw(_vary_case(title)) if category == "shared" else title
            generated_lines.append(f"{prefix} {gen_title}")
            generated_lines.append("")
            generated_lines.append(f"Isi baru BARU_{idx} bab ini.")
            generated_lines.append("")

        if category == "shared":
            shared.append((level, title, idx))
        elif category == "existing_only":
            existing_only.append((level, title, idx))
        else:
            generated_only.append((level, title, idx))

    return (
        "\n".join(existing_lines),
        "\n".join(generated_lines),
        shared,
        existing_only,
        generated_only,
    )


def _heading_keys(model: DraftModel):
    """Location keys (level, casefolded/trimmed title) for every heading."""
    return [
        (h.meta.get("level", 0), str(h.meta.get("text", "")).strip().casefold())
        for h in model.headings()
    ]


# =========================================================================== #
# Property 22: Pembaruan bab yang ada tanpa duplikasi lokasi
# =========================================================================== #
# Feature: automated-writing-workflow, Property 22: Pembaruan bab yang ada tanpa duplikasi lokasi
# Validates: Requirements 8.3
@settings(max_examples=200, deadline=None)
@given(data=_scenario())
def test_existing_chapter_updated_in_place_without_duplication(data):
    existing_md, generated_md, shared, existing_only, generated_only = data

    existing = DraftModel.from_markdown(existing_md)
    generated = DraftModel.from_markdown(generated_md)

    merged, _findings = merge(existing, generated)

    key_counts = Counter(_heading_keys(merged))
    merged_text = merged.to_markdown()

    # Every chapter present in the existing draft (shared or existing-only) that
    # matches a generated chapter is updated in place: it appears exactly once
    # (no duplicate copy created).
    for level, title, _idx in shared + existing_only:
        key = (level, title.strip().casefold())
        assert key_counts[key] == 1, (
            f"chapter {title!r} (level {level}) appears {key_counts[key]} times "
            f"after merge, expected exactly 1 (updated in place, not duplicated)"
        )

    # Shared chapters have their body updated in place: the new content wins and
    # the old content is superseded (no leftover duplicate body).
    for _level, _title, idx in shared:
        assert f"BARU_{idx}" in merged_text, (
            f"shared chapter idx {idx} was not updated with new content"
        )
        assert f"LAMA_{idx}" not in merged_text, (
            f"shared chapter idx {idx} still carries old content (duplicate/stale body)"
        )
        # And the new body must appear exactly once (no duplicated copy).
        assert merged_text.count(f"BARU_{idx}") == 1, (
            f"shared chapter idx {idx} new content appears "
            f"{merged_text.count(f'BARU_{idx}')} times, expected exactly 1"
        )

    # Existing-only chapters keep their original body untouched.
    for _level, _title, idx in existing_only:
        assert f"LAMA_{idx}" in merged_text, (
            f"existing-only chapter idx {idx} lost its content"
        )

    # Generated-only chapters are appended once (union), so they also appear once.
    for level, title, idx in generated_only:
        key = (level, title.strip().casefold())
        assert key_counts[key] == 1, (
            f"generated-only chapter {title!r} appears {key_counts[key]} times, "
            f"expected exactly 1"
        )
        assert f"BARU_{idx}" in merged_text
