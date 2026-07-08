"""Tests for the gantt [TABLE gantt] mode and ragged-row padding in
``build_table_element`` (scratch/merge_draft_to_docx.py).

Covers:
  * ragged rows (rows whose trailing empty cells were stripped) are padded to
    the full column count so the rendered table has no "hole" in the last
    column(s);
  * ``[TABLE gantt]`` mode replaces an "X" mark in a month column with an empty
    cell shaded (``w:shd@fill``) in a distinct per-activity (per data row)
    color, and removes the "X" text;
  * the legacy ``[TABLE]`` path (no mode) is unaffected: no shading, X kept.
"""
import sys
from pathlib import Path

import lxml.etree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
sys.path.insert(0, str(SCRATCH))

import merge_draft_to_docx as mrg  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def qn(tag):
    return f"{{{W}}}{tag}"


def rows_of(tbl):
    return tbl.findall("w:tr", NS)


def cells_of(tr):
    return tr.findall("w:tc", NS)


def cell_fill(tc):
    tcPr = tc.find("w:tcPr", NS)
    if tcPr is None:
        return None
    shd = tcPr.find("w:shd", NS)
    return None if shd is None else shd.get(qn("fill"))


def cell_text(tc):
    return "".join(t.text or "" for t in tc.iter(qn("t")))


# The real Tabel 1.2 shape: header + 6 activity rows, several with an empty
# trailing (Bulan 5) column that used to be dropped, producing the hole.
JADWAL_LINES = [
    "Aktivitas | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5",
    "Desain Arsitektur & UI | X |  |  |  |",
    "Pengembangan Backend |  | X | X |  |",
    "Pengembangan Frontend |  |  | X | X |",
    "Integrasi dan Pengujian Sistem |  |  |  | X | X",
    "Revisi Final & Penulisan Laporan |  |  |  |  | X",
    "Dokumentasi | X | X | X | X | X",
]


def test_ragged_rows_padded_no_hole():
    """Every row must have the full 6 cells even when trailing cells are empty."""
    item = {"type": "table", "lines": JADWAL_LINES, "mode": "gantt"}
    tbl = mrg.build_table_element(item)
    for tr in rows_of(tbl):
        assert len(cells_of(tr)) == 6, "ragged row left a hole in the table"


GANTT_FILL = "FCE4D6"  # uniform light orange


def test_gantt_colors_replace_x():
    """In gantt mode, X month cells become shaded empty cells using a single
    uniform light-orange fill; the activity-label column is never shaded."""
    item = {"type": "table", "lines": JADWAL_LINES, "mode": "gantt"}
    tbl = mrg.build_table_element(item)
    data_rows = rows_of(tbl)[1:]  # skip header

    shaded = 0
    for tr in data_rows:
        cells = cells_of(tr)
        # First column is the activity label: never shaded, keeps its text.
        assert cell_fill(cells[0]) is None
        assert cell_text(cells[0]) != ""
        for c in cells[1:]:
            if cell_fill(c) is not None:
                # Uniform light-orange fill, no "X" text anymore.
                assert cell_fill(c) == GANTT_FILL
                assert cell_text(c).strip() == ""
                shaded += 1

    assert shaded > 0, "gantt mode should shade the X month cells"

    # No cell anywhere still shows the literal X.
    for tr in data_rows:
        for c in cells_of(tr):
            assert cell_text(c).strip().upper() != "X"


def test_legacy_table_path_unchanged():
    """Without gantt mode, X marks are kept and no shading is applied."""
    item = {"type": "table", "lines": JADWAL_LINES, "mode": None}
    tbl = mrg.build_table_element(item)
    x_count = 0
    for tr in rows_of(tbl):
        for c in cells_of(tr):
            assert cell_fill(c) is None, "legacy [TABLE] must not add shading"
            if cell_text(c).strip().upper() == "X":
                x_count += 1
    assert x_count > 0, "legacy path should preserve the X marks"


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
