# Implementation Plan

## Overview

This plan fixes the brittle, content-specific table formatting in `format_all_tables()` (`skills/scripts/format_ta_proyek.py`) using the exploratory bugfix workflow: first write an exploration test that fails on the unfixed code (proving the bug), then write preservation tests that pass on the unfixed code (capturing behavior to keep), then apply the structure-driven fix, and finally re-run both to confirm the bug is resolved with no regressions.

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["1", "2"], "dependsOn": [] },
    { "wave": 2, "tasks": ["3.1", "3.2"], "dependsOn": ["1", "2"] },
    { "wave": 3, "tasks": ["3.3"], "dependsOn": ["3.1", "3.2"] },
    { "wave": 4, "tasks": ["3.4", "3.5"], "dependsOn": ["3.3"] },
    { "wave": 5, "tasks": ["4"], "dependsOn": ["3.4", "3.5"] }
  ]
}
```

- Tasks 1 and 2 must be completed BEFORE task 3 (tests written and run against unfixed code first).
- Task 3.4 depends on 3.1–3.3 and re-runs task 1's test.
- Task 3.5 depends on 3.1–3.3 and re-runs task 2's tests.
- Task 4 depends on all of task 3.

## Tasks

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Tables not fitted to printable width
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists (tables overflow the printable area because `format_all_tables` only normalizes the hardcoded `is_tabel_1_2` table)
  - **Scoped PBT Approach**: For deterministic OOXML shapes, scope the property to concrete failing cases derived from the design's examples; also generate random tables (varied `n_cols`, `n_rows`, optional pre-existing `tblGrid`, optional `gridSpan`) plus a body `sectPr` with the real page setup (`pgSz@w=11906`, `pgMar@left=2268`, `pgMar@right=1701` → printable = 7937 dxa)
  - Bug Condition (from design `isBugCondition`): for input `(tbl, page)` with `printable = page.width - page.left - page.right`, the bug holds when `totalTableWidth(tbl) != printable` OR `NOT hasFixedLayoutFittingPrintable(tbl, printable)` OR `NOT firstRowMarkedAsHeader(tbl)` OR `NOT hasConsistentBordersAndPadding(tbl)`
  - Test implementation details (from Bug Details + Examples in design):
    - Concrete case A — **Non-6-column overflow**: build a 4-column table, run current `format_all_tables`, assert total `tblPr/tblW@w == 7937` (type=dxa) and `sum(tblGrid/gridCol@w) == 7937`
    - Concrete case B — **Renamed first cell**: build a 6-column table whose first cell is `"Kegiatan"` (not `"Aktivitas"`), assert widths are normalized to 7937 dxa
    - Concrete case C — **Magic-number mismatch**: build the `"Aktivitas"` 6-column table, assert `sum(gridCol@w) == 7937` (unfixed sum is 8000 dxa from magic numbers `3500` + 5×`900`)
    - Concrete case D — **Missing header repeat / borders / padding**: any table, assert row 0 has `trPr/tblHeader` and `tblPr` has `tblBorders` and `tblCellMar`
    - Concrete case E — **Edge case, single-column table**: assert one `gridCol` at 7937 dxa and no crash
  - The test assertions should match the Expected Behavior Properties from design (Properties 1, 2, 3)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause (e.g., "4-column table has no `tblW`/`tblGrid` written", "`Aktivitas` table `gridCol` sums to 8000 dxa not 7937", "no `tblHeader`/`tblBorders`/`tblCellMar` on any table")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Existing table behaviors and other stages unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (behaviors outside width-fitting, header-repeat, borders, and padding — cases where `isBugCondition` returns false):
    - Observe: after `format_all_tables`, every table has `tblPr/jc == center`
    - Observe: header row (row 0) cells have `tcPr/vAlign == center` and `pPr/jc == center`
    - Observe: body cells have `pPr/ind` zeroed (`left=0 firstLine=0 right=0`) and `pPr` children obey `PPR_ORDER`
    - Observe: every `w:tbl` is processed/counted and the `Formatted N tables in document.xml.` summary is printed with correct N
    - Observe: running the full `format_document_xmls` pipeline leaves non-table content (paragraphs, drawings, `sectPr`/`pgSz`/`pgMar`, SDTs) identical
  - Write property-based tests capturing observed behavior patterns from the Preservation Requirements section (Property 4). Generate many table shapes (column counts, row counts, pre-existing grids, `gridSpan`) automatically to catch edge cases (empty grid, single column, ragged rows)
  - Property-based testing generates many test cases for stronger guarantees that non-width behaviors and other stages are unchanged
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix for brittle, content-specific table width normalization in `format_all_tables()`

  - [x] 3.1 Add pure helper `compute_printable_width(root, namespaces)`
    - Read the body `sectPr` (`w:body/w:sectPr`, falling back to the last `sectPr` in the body), extract `pgSz@w`, `pgMar@left`, `pgMar@right`, return `w − left − right`
    - Provide safe defaults matching the current setup (`w=11906`, `left=2268`, `right=1701` → `7937`) when values are missing or unparseable
    - Read-only: never mutate `sectPr`
    - _Bug_Condition: isBugCondition((tbl, page)) where printable = page.width − page.left − page.right_
    - _Expected_Behavior: expectedBehavior(result) — printable computed from document page setup (Property 1)_
    - _Preservation: page setup (`pgSz`/`pgMar`) read but not modified (Property 4)_
    - _Requirements: 2.1, 3.5_

  - [x] 3.2 Add pure helpers `column_ratios_from_grid(tbl, namespaces, n_cols)` and `distribute_width(printable, ratios)`
    - `column_ratios_from_grid`: use existing `tblGrid/gridCol@w` as proportions when present and their sum is positive; otherwise return even proportions (`1/n_cols`). Derive `n_cols` structurally as `len(tblGrid/gridCol)` when a grid exists, else the max `len(row.findall('w:tc'))` across rows, summing `w:tcPr/w:gridSpan` where present
    - `distribute_width`: return integer dxa widths that sum exactly to `printable` (multiply-and-floor per column, add the leftover remainder to the last column). Accept an optional `overrides` ratio list; handle `n_cols = 1`
    - No magic numbers; all widths computed from actual column count and printable width
    - _Bug_Condition: isBugCondition table with un-normalized/proportion-less widths_
    - _Expected_Behavior: expectedBehavior(result) — proportional distribution summing exactly to printable (Property 2)_
    - _Preservation: overrides are non-hardcoded and never keyed to cell text or column count (Property 4)_
    - _Requirements: 2.3_

  - [x] 3.3 Remove the content-specific special case and apply structure-driven table formatting
    - Delete the `is_tabel_1_2` probe (`len(first_row_cells) == 6` and `"Aktivitas"` check) and every branch keyed on it; detection becomes purely structural (rows/columns)
    - For each table set `tblPr/tblW` (`w = printable`, `type = dxa`), `tblPr/tblLayout` (`type = fixed`), keep `tblPr/jc = center`
    - Rewrite `tblGrid` so `gridCol@w` values equal the distributed widths (create `tblGrid` if absent); set each cell's `tcPr/tcW` (`type = dxa`) to its column width (respect `gridSpan` by summing spanned widths)
    - On row 0 set `trPr/tblHeader`; on `tblPr` set `tblBorders` (single-line, consistent size/color, all sides + insideH/insideV) and `tblCellMar` (consistent padding). Use `set_child_element` and keep `tblPr` children in valid OOXML order
    - Preserve existing per-cell loops: header-cell `vAlign=center` + `jc=center`, body-cell `jc=left`, `ind left/firstLine/right = 0`, `sort_element_children(pPr, PPR_ORDER)`; keep `tbl_count` increment and the final `print(f"  Formatted {tbl_count} tables in document.xml.")`
    - _Bug_Condition: isBugCondition((tbl, page)) holds for any table not fitted to printable / missing header/borders/padding_
    - _Expected_Behavior: expectedBehavior(result) — fixed layout, tblW == printable, gridCol/tcW sum == printable, row0 tblHeader, tblBorders + tblCellMar (Properties 1, 2, 3)_
    - _Preservation: centering, header-cell centering, body indentation clearing + PPR_ORDER, count/print unchanged (Property 4)_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.4 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Tables fitted to printable width
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied: `tblLayout == fixed`, `int(tblW@w) == printable` (type=dxa), `sum(gridCol@w) == printable`, `sum(tcW@w over one row honoring gridSpan) == printable`, row 0 has `trPr/tblHeader`, `tblPr` has `tblBorders` and `tblCellMar`, and no branch depends on cell text or a specific column count
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.5 Verify preservation tests still pass
    - **Property 2: Preservation** - Existing table behaviors and other stages unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions): `tblPr/jc == center`, header-cell centering, body-cell indentation clearing with valid `PPR_ORDER`, correct table count/summary print, and non-table content (paragraphs, drawings, `sectPr`/`pgSz`/`pgMar`, SDTs) identical
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Run the full test suite: exploration test (task 1), preservation tests (task 2), plus unit tests for `compute_printable_width`, `column_ratios_from_grid`, `distribute_width`, and integration tests over `format_document_xmls`
  - Confirm cross-branch shape coverage (2-, 4-, and 6-column tables representing `laporan/iman`, `laporan/dwikhi`, `laporan/faiz`) all receive uniform fit-to-printable treatment
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Property 1 (Bug Condition / Expected Behavior) and Property 2 (Preservation) use the `**Property N:**` format so hover status tracking works.
- Tests must be written and run against the UNFIXED code first: task 1 must FAIL, task 2 must PASS. This confirms the bug exists and captures the baseline before any code change.
- The fix is scoped entirely to `format_all_tables()` and new pure helpers in `skills/scripts/format_ta_proyek.py`; no other function is modified.
- `format_ta_proyek.py` is a shared script across `laporan/iman`, `laporan/dwikhi`, `laporan/faiz` — the fix must stay content-agnostic (structure-driven only, never keyed on cell text or a specific column count).
- Do not modify `pgSz`/`pgMar`; the fix only reads page setup to compute printable width.
