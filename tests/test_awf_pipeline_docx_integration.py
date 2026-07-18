"""Integration test: kompatibilitas keluaran ``run_alur`` dengan pipeline ``.docx``.

Spec: .kiro/specs/automated-writing-workflow (task 16.3 — integration test, BUKAN PBT).

Validates: Requirements 7.2

Tujuan test ini adalah membuktikan bahwa Markdown yang dihasilkan oleh
``alur_penulisan.pipeline.run_alur`` tetap **kompatibel** dengan tahap format
``.docx`` yang sudah ada, yaitu ``skills/scripts/merge_draft_to_docx.py``. Kita:

* Menjalankan ``run_alur`` pada beberapa skenario draf (draf kosong, draf dengan
  daftar berjenjang, draf dengan blok tabel) melalui *hook* baca/tulis in-memory
  dan ``FactStore`` in-memory sehingga tidak ada berkas nyata yang disentuh.
* Mengumpankan ``draft_text`` hasilnya ke ``merge_draft_to_docx.parse_markdown``
  dan memverifikasi parsing berhasil tanpa error serta struktur item terparse
  sesuai harapan (heading, list_item, table).
* Memverifikasi indentasi daftar keluaran = 3 spasi/level, sehingga
  ``compute_list_level`` menghasilkan level yang sama dengan struktur logis
  (selaras ``LIST_INDENT_UNIT == 3``).

Test ini TIDAK menjalankan ``build_pipeline.py`` penuh dan TIDAK memodifikasi
tahap format ``.docx`` — ia hanya mengonsumsi fungsi parser murni dari
``merge_draft_to_docx.py``.
"""
import sys
from pathlib import Path

import pytest

# --------------------------------------------------------------------------- #
# Path setup: expose skills/scripts so both the workflow package and the format
# consumer can be imported.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.pipeline import run_alur, RunStatus  # noqa: E402
from alur_penulisan.fact_verifier import FactStore  # noqa: E402
import merge_draft_to_docx as docx  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _run_with_input(draft_in: str) -> "tuple[str, str]":
    """Run ``run_alur`` on ``draft_in`` via in-memory hooks.

    Uses an in-memory read/write hook (no real file touched) and an in-memory,
    accessible :class:`FactStore` (no ``project_facts.json`` read). The active
    branch is ``laporan/iman`` so the Peran_Branch resolves and the run reaches
    COMPLETED. Returns ``(status_value, draft_text)``.
    """
    store = {"draft": draft_in}

    def read(_path: str) -> str:
        return store["draft"]

    def write(_path: str, text: str) -> None:
        store["draft"] = text

    result = run_alur(
        "Tugas_Akhir_Draft.md",
        active_branch="laporan/iman",
        read=read,
        write=write,
        load_facts=lambda _p: FactStore.from_mapping({}),
    )
    assert result.status is RunStatus.COMPLETED
    assert result.draft_text is not None
    return result.status.value, result.draft_text


def _parse_output(tmp_path: Path, draft_text: str, name: str) -> list:
    """Write ``draft_text`` to a temp file and parse it with the format stage.

    ``parse_markdown`` reads from a path, so the workflow output is persisted to
    an isolated temp file first. Returns the parsed item list.
    """
    md_file = tmp_path / name
    md_file.write_text(draft_text, encoding="utf-8")
    return docx.parse_markdown(str(md_file))


# Draft scenarios fed through the in-memory read hook.
_EMPTY_DRAFT = ""

_NESTED_LIST_DRAFT = """# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Berikut daftar berjenjang dengan indentasi 3 spasi per level:

1. Item tingkat satu
   a. Item tingkat dua
   b. Item tingkat dua lainnya
      1) Item tingkat tiga
2. Item tingkat satu kedua
"""

_TABLE_DRAFT = """# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Tabel 1.1 menyajikan ringkasan data proyek.

[TABLE]
Kolom A | Kolom B
1 | 2
3 | 4
[/TABLE]
"""


# --------------------------------------------------------------------------- #
# Scenario 1: empty draft -> generated skeleton parses cleanly.
# --------------------------------------------------------------------------- #
def test_empty_draft_output_parses_and_has_expected_headings(tmp_path):
    status, draft_text = _run_with_input(_EMPTY_DRAFT)
    assert status == "completed"

    items = _parse_output(tmp_path, draft_text, "empty.md")

    # Parsing succeeds and yields a non-empty structured item list.
    assert isinstance(items, list)
    assert items, "parse_markdown returned no items for the generated skeleton"

    # The four canonical chapters (BAB I-IV) are present as level-1 headings, in
    # order, so the format stage sees a well-formed chapter structure (Req 7.2).
    headings = [it for it in items if it["type"] == "heading"]
    bab_titles = [h["text"] for h in headings if h["level"] == 1]
    assert bab_titles == [
        "BAB I PENDAHULUAN",
        "BAB II RANCANGAN PROYEK",
        "BAB III IMPLEMENTASI PROYEK",
        "BAB IV PENUTUP",
    ]

    # Every parsed item carries a recognized type (no malformed/unknown item).
    known = {"heading", "paragraph", "list_item", "table", "page_break", "code_block"}
    assert all(it["type"] in known for it in items)


# --------------------------------------------------------------------------- #
# Scenario 2: nested list -> 3 spaces/level; compute_list_level == logical level.
# --------------------------------------------------------------------------- #
def test_nested_list_output_uses_three_space_indent_per_level(tmp_path):
    status, draft_text = _run_with_input(_NESTED_LIST_DRAFT)
    assert status == "completed"

    # The workflow preserves the nested list verbatim: raw output lines keep the
    # 3-space-per-level indentation grammar that the format stage relies on.
    line_indent = {}
    for raw in draft_text.splitlines():
        marker = raw.strip().split(" ", 1)[0] if raw.strip() else ""
        if marker in {"1.", "a.", "b.", "1)", "2."}:
            line_indent[raw.strip()] = len(raw) - len(raw.lstrip(" "))
    # 1. -> level 1 (0 spaces), a./b. -> level 2 (3 spaces), 1) -> level 3 (6).
    assert line_indent["1. Item tingkat satu"] == 0
    assert line_indent["2. Item tingkat satu kedua"] == 0
    assert line_indent["a. Item tingkat dua"] == 3
    assert line_indent["b. Item tingkat dua lainnya"] == 3
    assert line_indent["1) Item tingkat tiga"] == 6

    items = _parse_output(tmp_path, draft_text, "nested_list.md")

    # Collect the list items belonging to our known markers, in reading order.
    list_items = [it for it in items if it["type"] == "list_item"]
    by_text = {it["text"]: it for it in list_items}
    for expected in (
        "Item tingkat satu",
        "Item tingkat dua",
        "Item tingkat dua lainnya",
        "Item tingkat tiga",
        "Item tingkat satu kedua",
    ):
        assert expected in by_text, f"list item hilang saat parsing: {expected!r}"

    # The level assigned by the format stage matches the logical nesting depth,
    # confirming 3-space indentation maps 1:1 to structural levels (Req 7.2).
    assert by_text["Item tingkat satu"]["level"] == 1
    assert by_text["Item tingkat dua"]["level"] == 2
    assert by_text["Item tingkat dua lainnya"]["level"] == 2
    assert by_text["Item tingkat tiga"]["level"] == 3
    assert by_text["Item tingkat satu kedua"]["level"] == 1

    # And the pure indentation rule agrees for 3 spaces/level given LIST_INDENT_UNIT.
    assert docx.LIST_INDENT_UNIT == 3
    assert docx.compute_list_level(0, "1.") == 1
    assert docx.compute_list_level(3, "a.") == 2
    assert docx.compute_list_level(6, "1)") == 3


# --------------------------------------------------------------------------- #
# Scenario 3: table block survives and parses as a table item.
# --------------------------------------------------------------------------- #
def test_table_draft_output_parses_as_table_item(tmp_path):
    status, draft_text = _run_with_input(_TABLE_DRAFT)
    assert status == "completed"

    # The [TABLE] block is preserved verbatim by the workflow.
    assert "[TABLE]" in draft_text
    assert "[/TABLE]" in draft_text

    items = _parse_output(tmp_path, draft_text, "table.md")

    tables = [it for it in items if it["type"] == "table"]
    assert tables, "blok [TABLE] tidak terparse sebagai item tabel"
    # The table body rows are captured (header + two data rows).
    first = tables[0]
    assert "Kolom A | Kolom B" in first["lines"]
    assert "1 | 2" in first["lines"]
    assert "3 | 4" in first["lines"]
