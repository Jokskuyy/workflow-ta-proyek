"""Document-level preservation property test for the writing-pipeline-improvements
spec (WPI Task 11.1).

Spec: .kiro/specs/writing-pipeline-improvements

Covers design Property 16 — *Preservasi lintas-area Opt_In_By_Content (tingkat
dokumen)*:

  Untuk setiap Draf yang TIDAK memuat Konstruk_Baru (tanpa kode inline `` `..` ``,
  tautan ``[t](u)``, ``***``, ``\\*``, maupun Tabel_Pipa ``|``), keluaran lengkap
  Tahap_Penulisan identik BYTE-PER-BYTE dengan Output_Baseline untuk Draf tersebut.

Strategy (design §Testing Strategy / baseline-equivalence):
  A synthetic draft is generated using ONLY legacy constructs (headings, plain
  paragraphs, balanced ``**bold**`` / ``*italic*``, ``[TABLE]`` bracket tables,
  outermost-level list items, code blocks, page breaks). The draft is parsed with
  the production ``parse_markdown`` and the full body element stream is assembled
  exactly as ``merge_draft_to_xml`` routes items to the element builders.

  Two renderings are produced and compared byte-for-byte:

    * NEW      — the current production builders (``build_p_element``,
                 ``build_table_element``, ``build_code_block_elements`` which call
                 the refactored ``add_formatted_text`` = tokenize_inline + emit_runs).
    * BASELINE — the same assembly, but the only NEW-construct-capable functions
                 (``add_formatted_text`` and ``build_table_element``) are swapped
                 for the FROZEN oracle copies in
                 ``tests/fixtures/oracle_writing.py`` (Task 1.2).

  Because no new constructs are present, the two renderings MUST be identical.
  This integrates the run-level (Property 8) and table-level (Property 11)
  preservation guarantees across a whole document: item ordering, heading/list/
  caption routing, default (non-numPr) list rendering, code blocks and page
  breaks all preserved.

Pure transform + small temp-file parse per example, so 100+ Hypothesis
iterations stay cheap.

# Feature: writing-pipeline-improvements, Property 16: Preservasi lintas-area
# Opt_In_By_Content (tingkat dokumen).
"""
import string
import sys
import tempfile
from pathlib import Path

import lxml.etree
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the production Mesin_Merge script + the frozen oracle.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SCRATCH))
sys.path.insert(0, str(FIXTURES))

import merge_draft_to_docx as mrg  # noqa: E402
import oracle_writing as oracle  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Alphabet deliberately excludes every NEW-construct trigger and every Markdown
# control character so generated content is unambiguously "legacy only":
#   no '*' '`' '[' ']' '(' ')' '\\' '|' '#' '-' '.'
_WORD_ALPHABET = string.ascii_letters + string.digits


def _oracle_add_formatted_text(p_elem, text, default_rPr=None, rel_manager=None):
    """rel_manager-tolerant adapter over the frozen oracle add_formatted_text.

    The legacy oracle has no ``rel_manager`` parameter (links are a NEW
    construct and never appear in this test's drafts), so it is simply ignored.
    """
    oracle.oracle_add_formatted_text(p_elem, text, default_rPr)


# --------------------------------------------------------------------------- #
# Strategies — legacy-only draft fragments.
# --------------------------------------------------------------------------- #
_word = st.text(alphabet=_WORD_ALPHABET, min_size=1, max_size=6)
_words = st.lists(_word, min_size=1, max_size=4).map(lambda ws: " ".join(ws))


@st.composite
def _inline_text(draw):
    """A line of inline text: plain words and balanced **bold** / *italic*
    fragments separated by spaces. No '***', no '\\*', no code/link/pipe."""
    nfrag = draw(st.integers(min_value=1, max_value=4))
    frags = []
    for _ in range(nfrag):
        kind = draw(st.sampled_from(["plain", "bold", "italic"]))
        body = draw(_words)
        if kind == "bold":
            frags.append(f"**{body}**")
        elif kind == "italic":
            frags.append(f"*{body}*")
        else:
            frags.append(body)
    return " ".join(frags)


@st.composite
def _heading_block(draw):
    level = draw(st.integers(min_value=2, max_value=4))
    return ("#" * level) + " " + draw(_words)


@st.composite
def _paragraph_block(draw):
    return draw(_inline_text())


@st.composite
def _list_block(draw):
    """One or more outermost (indent-0) list items. Marker is cosmetic."""
    n = draw(st.integers(min_value=1, max_value=4))
    lines = []
    for k in range(n):
        marker = draw(st.sampled_from([f"{k + 1}.", f"{k + 1})", "a.", "b.", "a)"]))
        lines.append(f"{marker} {draw(_inline_text())}")
    return "\n".join(lines)


@st.composite
def _bracket_table_block(draw):
    """A legacy [TABLE]...[/TABLE] block (never a pipe table)."""
    nrows = draw(st.integers(min_value=1, max_value=4))
    ncols = draw(st.integers(min_value=1, max_value=4))
    rows = []
    for _ in range(nrows):
        cells = [draw(_words) for _ in range(ncols)]
        rows.append("| " + " | ".join(cells) + " |")
    return "[TABLE]\n" + "\n".join(rows) + "\n[/TABLE]"


@st.composite
def _code_block(draw):
    nlines = draw(st.integers(min_value=1, max_value=3))
    lines = [draw(_words) for _ in range(nlines)]
    return "```\n" + "\n".join(lines) + "\n```"


_PAGE_BREAK = st.just("---")


@st.composite
def _synthetic_draft(draw):
    """Assemble a legacy-only draft. Always starts with the BAB I heading so
    parse_markdown begins collecting (everything before BAB I is ignored)."""
    nblocks = draw(st.integers(min_value=0, max_value=6))
    blocks = ["# BAB I " + draw(_words)]
    for _ in range(nblocks):
        block = draw(st.one_of(
            _heading_block(),
            _paragraph_block(),
            _list_block(),
            _bracket_table_block(),
            _code_block(),
            _PAGE_BREAK,
        ))
        blocks.append(block)
    return "\n\n".join(blocks) + "\n"


# --------------------------------------------------------------------------- #
# Body assembly — mirrors merge_draft_to_xml item routing (no template merge).
# --------------------------------------------------------------------------- #
def _assemble(items, *, table_builder, aft):
    """Serialize the body element stream for ``items`` using the given table
    builder and ``add_formatted_text`` implementation (monkeypatched on the
    module so the shared ``build_p_element`` picks it up)."""
    orig_aft = mrg.add_formatted_text
    mrg.add_formatted_text = aft
    try:
        parts = []
        for item in items:
            t = item["type"]
            if t in ("heading", "page_break", "list_item", "paragraph"):
                parts.append(lxml.etree.tostring(mrg.build_p_element(item)))
            elif t == "code_block":
                parts.extend(lxml.etree.tostring(e)
                             for e in mrg.build_code_block_elements(item))
            elif t == "table":
                parts.append(lxml.etree.tostring(table_builder(item)))
        return b"\n".join(parts)
    finally:
        mrg.add_formatted_text = orig_aft


def _parse_draft(text):
    """Write the draft to a temp file and parse it with the production parser."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(text)
        tmp_path = fh.name
    try:
        return mrg.parse_markdown(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# --------------------------------------------------------------------------- #
# Property 16.
# --------------------------------------------------------------------------- #
# Feature: writing-pipeline-improvements, Property 16: Preservasi lintas-area
# Opt_In_By_Content (tingkat dokumen) — untuk Draf tanpa Konstruk_Baru, keluaran
# lengkap Tahap_Penulisan identik byte-per-byte dengan Output_Baseline.
# Validates: Requirements 5.6, 7.7
@settings(max_examples=150)
@given(draft=_synthetic_draft())
def test_property16_document_level_preservation(draft):
    items = _parse_draft(draft)

    # Sanity: a legacy-only draft must never produce a pipe table or a numbered
    # (numPr) list item, and must contain no hyperlink/code-inline runs.
    for it in items:
        if it["type"] == "table":
            assert "alignments" not in it and not it.get("is_pipe")
        if it["type"] == "list_item":
            assert not it.get("use_numpr")

    new_xml = _assemble(items,
                        table_builder=mrg.build_table_element,
                        aft=mrg.add_formatted_text)
    baseline_xml = _assemble(items,
                            table_builder=oracle.oracle_build_table_element,
                            aft=_oracle_add_formatted_text)

    assert new_xml == baseline_xml


# --------------------------------------------------------------------------- #
# Unit anchors — concrete legacy drafts stay byte-identical to the baseline path.
# --------------------------------------------------------------------------- #
def test_doc_preservation_mixed_legacy_draft():
    draft = (
        "# BAB I PENDAHULUAN\n\n"
        "Paragraf biasa dengan **tebal** dan *miring*.\n\n"
        "## Sub Bagian\n\n"
        "1. Item pertama\n"
        "2. Item kedua dengan *penekanan*\n\n"
        "[TABLE]\n"
        "| Kolom A | Kolom B |\n"
        "| nilai 1 | nilai 2 |\n"
        "[/TABLE]\n\n"
        "---\n\n"
        "Paragraf penutup.\n"
    )
    items = _parse_draft(draft)
    assert any(it["type"] == "table" for it in items)
    assert any(it["type"] == "page_break" for it in items)

    new_xml = _assemble(items,
                        table_builder=mrg.build_table_element,
                        aft=mrg.add_formatted_text)
    baseline_xml = _assemble(items,
                            table_builder=oracle.oracle_build_table_element,
                            aft=_oracle_add_formatted_text)
    assert new_xml == baseline_xml


def test_doc_preservation_empty_body_when_no_bab():
    # Without a "# BAB I" trigger nothing is collected (preserved behavior).
    items = _parse_draft("Just a cover line.\nAnother line.\n")
    assert items == []
