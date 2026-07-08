# Table Formatting Fix Bugfix Design

## Overview

`format_all_tables(root, namespaces)` in `skills/scripts/format_ta_proyek.py` walks every `w:tbl` in `document.xml` and applies formatting. Today it does two different things depending on a hardcoded content probe:

- Every table gets: table centering (`tblPr/jc = center`), per-cell vertical alignment, header-cell horizontal centering, body-cell left alignment, and paragraph indentation clearing.
- Exactly one table — the one with exactly 6 columns whose first cell text contains the literal word `"Aktivitas"` (assumed to be "Tabel 1.2 / Jadwal Kegiatan") — additionally gets `tblGrid`/`tcW` width normalization, using magic numbers (first column `3500` dxa, five more columns at `900` dxa via a fixed `range(5)`).

The consequence: any table that is not that exact shape receives **no width normalization**, so wide tables overflow the printable page margins. This is inconsistent with image handling in the same script, which scales drawings to a printable bounding box. The detection is also fragile — renaming `"Aktivitas"` or changing the column count silently disables the only working case (`is_tabel_1_2` becomes `False`).

Because `format_ta_proyek.py` is a **shared** script across `laporan/iman`, `laporan/dwikhi`, and `laporan/faiz`, the fix must be general and content-agnostic. The strategy is to replace the content-specific special-case with a structure-driven formatter that, for **every** table:

1. Computes the printable width once from the document's own page setup (`pgSz` width minus left/right `pgMar`).
2. Fits the total table width to that printable width (`tblW type=dxa`, `tblLayout=fixed`).
3. Distributes the printable width across columns proportionally — derived from the table's existing `tblGrid` proportions where available, otherwise split evenly — writing both `tblGrid/gridCol` and per-cell `tcW`.
4. Supports optional, non-hardcoded per-column width overrides (a caller-supplied ratio list), never keyed on cell text or column count.
5. Marks the first row as a repeating header (`tblHeader`) and applies consistent borders, cell padding, and alignment.

All existing preserved behaviors (centering, header-cell centering, body-cell indentation clearing, OOXML child ordering, table counting/reporting, and every other formatting stage) remain unchanged.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug — a table exists whose total width is not normalized to the printable area (any table other than the single hardcoded `is_tabel_1_2` match), allowing it to overflow the page margins.
- **Property (P)**: The desired behavior — every table's total width fits the printable area, with columns sized proportionally from the table's own structure (or evenly), plus header-row repeat and consistent alignment/borders/padding.
- **Preservation**: Behaviors that must remain byte-for-byte equivalent for inputs outside the bug's scope — table centering, header-cell centering, body-cell indentation clearing, OOXML child ordering, table counting/reporting, and all other formatting stages.
- **`format_all_tables(root, namespaces)`**: The function in `skills/scripts/format_ta_proyek.py` that iterates every `w:tbl` in `document.xml` and applies table formatting. This is the sole function in scope.
- **`is_tabel_1_2`**: The current boolean flag (to be removed) that content-detects one table via `len(first_row_cells) == 6` AND `"Aktivitas" in first_cell_text`.
- **Printable width**: `pgSz@w − pgMar@left − pgMar@right`, expressed in twips/dxa (1/1440 inch). With the document's page setup (`w=11906`, `left=2268`, `right=1701`) this is `11906 − 2268 − 1701 = 7937` dxa.
- **`tblGrid` / `gridCol`**: OOXML elements defining a table's column grid; each `gridCol@w` is a column width in dxa.
- **`tcW`**: Per-cell preferred width (`w:tcPr/w:tcW`, `type=dxa`).
- **`tblHeader`**: `w:trPr/w:tblHeader`, marks a row as a header that repeats on each page.
- **`set_child_element` / `sort_element_children` / `PPR_ORDER`**: Existing helpers used to create-or-update child elements and to keep OOXML child ordering schema-valid.

## Bug Details

### Bug Condition

The bug manifests when a table is present in `document.xml` whose total width is left un-normalized, so it can exceed the printable area. Under the current implementation this is **every table except** the one that happens to have exactly 6 columns with `"Aktivitas"` in its first cell. The `format_all_tables` function is either skipping width normalization entirely (no `tblW`, no `tblGrid` rewrite, no `tcW`) or applying width normalization only via content-specific special-casing rather than from the table's structure and the page's printable width.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input = (tbl, page) where
           tbl  is a w:tbl element with n_cols >= 1 and n_rows >= 1,
           page = (page_width_dxa, margin_left_dxa, margin_right_dxa)
  OUTPUT: boolean

  printable := page.page_width_dxa - page.margin_left_dxa - page.margin_right_dxa

  RETURN totalTableWidth(tbl) != printable
         OR NOT hasFixedLayoutFittingPrintable(tbl, printable)
         OR NOT firstRowMarkedAsHeader(tbl)
         OR NOT hasConsistentBordersAndPadding(tbl)
END FUNCTION
```

Equivalently, in terms of the current code: the bug condition holds for any table where `is_tabel_1_2` is `False` (no width handling at all), and also for the `is_tabel_1_2` table itself because its widths come from magic numbers rather than the printable width and its structure, and no table receives `tblHeader`, borders, or padding.

### Examples

- A 4-column comparison table (not 6 columns): current code applies no `tblGrid`/`tcW`, so with wide content it overflows the right margin. Expected: total width fitted to 7937 dxa, columns ~1984 dxa each.
- A 6-column "Jadwal Kegiatan" table with first cell `"Aktivitas"`: current code sets first column `3500` and five columns `900` (sum = 8000 dxa), which is not derived from the 7937 dxa printable width and ignores the real grid. Expected: total fitted to 7937 dxa, distributed proportionally from the table's own `tblGrid` (or evenly).
- The same 6-column table after an author renames `"Aktivitas"` to `"Kegiatan"`: current code silently stops normalizing (`is_tabel_1_2` becomes `False`) and the table overflows. Expected: identical fit-to-printable treatment, because detection no longer depends on cell text.
- A 2-column table authored on `laporan/dwikhi` (ERD attributes): current code applies no width normalization. Expected: total fitted to 7937 dxa, two columns ~3968/3969 dxa; first row marked `tblHeader`; borders and padding applied.
- Edge case — a single-column table: expected one column at the full 7937 dxa, no crash, header repeat set on row 0.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Tables continue to be centered horizontally via `tblPr/jc = center` (Requirement 3.1).
- Header row (row 0) cells continue to be centered both vertically (`tcPr/vAlign = center`) and horizontally (`pPr/jc = center`) (Requirement 3.2).
- Body cells continue to have paragraph indentation cleared (`ind left=0 firstLine=0 right=0`) and continue to maintain valid OOXML child ordering via `sort_element_children(pPr, PPR_ORDER)` (Requirement 3.3).
- `format_all_tables` continues to process and count every `w:tbl` in `document.xml` and to print the number of tables formatted (Requirement 3.4).
- All other formatting stages (numbering, images, captions, bibliography, headings, section/page setup) continue to behave exactly as before — this fix is scoped only to `format_all_tables()` (Requirement 3.5).

**Scope:**
Anything that does NOT concern table width fitting, header-row repeat, borders, or cell padding must be completely unaffected. This includes:
- Every non-table element in `document.xml` (paragraphs, drawings, SDTs, section properties).
- All other functions in `format_ta_proyek.py` and their call order in `format_document_xmls`.
- The page setup itself (`pgSz`/`pgMar`) — the fix reads it but must not modify it.

**Note:** The expected correct behavior for buggy inputs is defined in the Correctness Properties section (Properties 1–3). This section focuses on what must NOT change.

## Hypothesized Root Cause

Based on the bug analysis, the defect stems from content-specific special-casing rather than structure-driven formatting:

1. **Content-based detection instead of structural detection**: `is_tabel_1_2` is computed from `len(first_row_cells) == 6` AND `"Aktivitas" in first_cell_text`. This scopes width normalization to a single table identified by its text and column count, so any other table (or the same table after edits) gets no normalization. This is the direct cause of overflow for all other tables (Defect 1.1, 1.2).

2. **Hardcoded magic-number widths**: Even for the detected table, widths come from literals (`3500`, `900`, `range(5)`) that sum to 8000 dxa and do not derive from the printable width (7937 dxa) or the table's actual column count. There is no computation from page geometry (Defect 1.3).

3. **No total-width / layout control**: The code never sets `tblW` (total table preferred width) or `tblLayout=fixed`, so Word is free to autofit and overflow. `tcW`/`gridCol` alone, without a fixed layout and matching total, do not guarantee fit (Defect 1.1, 1.4).

4. **Missing table-level formatting**: No `tblHeader` (header repeat), no `tblBorders`, and no `tblCellMar` (cell padding) are ever applied to any table (Defect 1.4).

The fix replaces items 1–4 with a single structure-driven path that computes printable width from the document's section properties and applies uniform table-level and column-level width settings to every table.

## Correctness Properties

Property 1: Bug Condition - Total table width fits the printable area

_For any_ table (any column count, any cell content) and the document's page setup, the fixed `format_all_tables` SHALL set the table to a fixed layout (`tblPr/tblLayout = fixed`) with a total preferred width (`tblPr/tblW type=dxa`) equal to the printable width (`pgSz@w − pgMar@left − pgMar@right`), and the sum of `tblGrid/gridCol@w` (and correspondingly `tcW`) SHALL equal that printable width, so the table does not overflow the page margins. Detection and formatting SHALL depend only on table structure (rows/columns), never on cell text or a specific column count.

**Validates: Requirements 2.1, 2.2**

Property 2: Bug Condition - Proportional, non-hardcoded column distribution

_For any_ table, the fixed function SHALL distribute the printable width across columns proportionally: when the table's existing `tblGrid` has positive column widths, each new `gridCol@w` SHALL be `printable × (oldWidth_i / sum(oldWidths))`; otherwise the width SHALL be split evenly across the actual column count. All widths SHALL be computed from the actual column count and printable width (no magic numbers), the per-column widths SHALL sum exactly to the printable width (remainder assigned deterministically to the last column), and an optional caller-supplied ratio list MAY override the distribution without being keyed to any specific table's text or column count.

**Validates: Requirements 2.3**

Property 3: Bug Condition - Header repeat and consistent table formatting

_For any_ table, the fixed function SHALL mark the first row as a repeating header (`trPr/tblHeader`) and SHALL apply consistent table borders (`tblPr/tblBorders`) and cell padding (`tblPr/tblCellMar`) to every table, with all created/updated elements kept in valid OOXML child order.

**Validates: Requirements 2.4**

Property 4: Preservation - Existing behaviors and other stages unchanged

_For any_ input where the bug condition does NOT hold (i.e., all behaviors outside width-fitting, header-repeat, borders, and padding), the fixed code SHALL produce the same result as the original code, preserving: table centering (`tblPr/jc=center`), header-cell vertical+horizontal centering, body-cell indentation clearing with valid `PPR_ORDER`, processing and counting of every `w:tbl` with the same summary print, and identical behavior of all other formatting stages (numbering, images, captions, bibliography, headings, section/page setup).

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

The change is scoped entirely to `format_all_tables()` and adds small pure helpers. No other function is modified.

**File**: `skills/scripts/format_ta_proyek.py`

**Function**: `format_all_tables(root, namespaces)` (plus new helpers)

**Specific Changes**:

1. **Compute printable width from the document's page setup**: Add a pure helper `compute_printable_width(root, namespaces)` that reads the body `sectPr` (`w:body/w:sectPr`, falling back to the last `sectPr` in the body if needed), extracts `pgSz@w`, `pgMar@left`, `pgMar@right`, and returns `w − left − right`. Provide safe defaults matching the current setup (`w=11906`, `left=2268`, `right=1701` → `7937`) when values are missing or unparseable. This helper only reads; it never mutates `sectPr` (Requirement 3.5).

2. **Remove the content-specific special case**: Delete the `is_tabel_1_2` probe (`len(first_row_cells) == 6` and `"Aktivitas"` check) and every branch keyed on it. Detection becomes purely structural: number of columns and rows.

3. **Determine column count and proportions from structure**: Add a pure helper `column_ratios_from_grid(tbl, namespaces, n_cols)`:
   - Read existing `tblGrid/gridCol@w`. If present and their sum is positive, use them as proportions.
   - Otherwise return even proportions (`1/n_cols` each).
   - `n_cols` is derived structurally as `len(tblGrid/gridCol)` when a grid exists, else the maximum `len(row.findall('w:tc'))` across rows (accounting for `w:tcPr/w:gridSpan` when present, summing spans).

4. **Distribute printable width without magic numbers**: Add a pure helper `distribute_width(printable, ratios)` that returns a list of integer dxa widths that sum exactly to `printable` (multiply-and-floor per column, then add the leftover remainder to the last column so the total is exact). Accept an optional `overrides` ratio list parameter on the formatter path so callers can supply non-hardcoded per-column ratios; when omitted, use `column_ratios_from_grid`.

5. **Apply total width and fixed layout at the table level**: For each table set `tblPr/tblW` (`w = printable`, `type = dxa`), `tblPr/tblLayout` (`type = fixed`), and keep `tblPr/jc = center` (unchanged). Rewrite `tblGrid` so its `gridCol@w` values are exactly the distributed widths (creating `tblGrid` if absent). Set each cell's `tcPr/tcW` (`type = dxa`) to the width of the column it occupies (respecting `gridSpan` by summing the spanned column widths).

6. **Apply header repeat, borders, and cell padding**: On row 0, set `trPr/tblHeader`. On `tblPr`, set `tblBorders` (single-line, consistent size/color for top/left/bottom/right/insideH/insideV) and `tblCellMar` (consistent top/left/bottom/right padding). Use `set_child_element` and keep `tblPr` children in a valid order.

7. **Preserve all existing per-cell behavior**: Keep the existing loops that set header-cell `vAlign=center` + `jc=center`, body-cell `jc` (now uniformly `left` for body cells, since the `is_tabel_1_2`-only `center` branch is removed), `ind left/firstLine/right = 0`, and `sort_element_children(pPr, PPR_ORDER)`. Keep the `tbl_count` increment and the final `print(f"  Formatted {tbl_count} tables in document.xml.")` exactly as-is (Requirement 3.4).

Notes on preservation semantics: today body cells in the `is_tabel_1_2` table (columns > 0) are centered; after the fix all body cells are left-aligned uniformly. This is an intended generalization consistent with the requirement to stop special-casing by content (Requirement 2.2), and the preservation contract (Property 4) covers only behaviors outside width/header/borders/padding for tables that are not the removed special case. All non-table behavior and other stages remain identical.

## Testing Strategy

### Validation Approach

Two phases: first surface counterexamples that demonstrate the bug on the current (unfixed) code, then verify the fix works for all tables and preserves the behaviors that must not change. Because the unit under test manipulates OOXML via `lxml`, tests build small in-memory `w:tbl`/`w:body` fragments and assert on the resulting XML.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix, and confirm or refute the root-cause hypothesis. If refuted, re-hypothesize.

**Test Plan**: Construct tables of varying shapes plus a body `sectPr` with the real page setup, run the current `format_all_tables`, and assert the expected fit-to-printable outcome. On unfixed code these assertions fail, exposing the defect.

**Test Cases**:
1. **Non-6-column overflow**: A 4-column table — assert total `tblW` equals printable (7937 dxa) and `gridCol` sum equals printable (will fail on unfixed code — no `tblW`/`tblGrid` written).
2. **Renamed first cell**: A 6-column table whose first cell is `"Kegiatan"` (not `"Aktivitas"`) — assert widths are normalized (will fail on unfixed code — `is_tabel_1_2` is `False`).
3. **Magic-number mismatch**: The `"Aktivitas"` 6-column table — assert `gridCol` sum equals 7937 dxa (will fail on unfixed code — sum is 8000 dxa from magic numbers).
4. **Missing header repeat / borders / padding**: Any table — assert row 0 has `trPr/tblHeader` and `tblPr` has `tblBorders` and `tblCellMar` (will fail on unfixed code — none are set).
5. **Edge case — single-column table**: assert one `gridCol` at 7937 dxa and no crash (may fail on unfixed code).

**Expected Counterexamples**:
- No `tblW`/`tblLayout` and no `tblGrid`/`tcW` for any table other than the hardcoded 6-column `"Aktivitas"` match.
- For the matched table, `gridCol` widths sum to 8000 dxa, not the 7937 dxa printable width.
- No `tblHeader`, `tblBorders`, or `tblCellMar` on any table.
- Possible causes: content-based `is_tabel_1_2` detection, hardcoded magic numbers, missing total-width/layout control, missing table-level formatting.

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL (tbl, page) WHERE isBugCondition((tbl, page)) DO
  printable := page.width - page.left - page.right
  format_all_tables(root_containing(tbl, page), namespaces)
  ASSERT tblPr/tblLayout == 'fixed'
  ASSERT int(tblPr/tblW@w) == printable AND tblPr/tblW@type == 'dxa'
  ASSERT sum(gridCol@w) == printable
  ASSERT sum(tcW@w over one row, honoring gridSpan) == printable
  ASSERT row0 has trPr/tblHeader
  ASSERT tblPr has tblBorders AND tblCellMar
  ASSERT no branch depends on cell text or a specific column count
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT format_all_tables_original(input) == format_all_tables_fixed(input)
END FOR
```

For table-scoped behaviors this means, for every table: `tblPr/jc == center`, header cells keep `vAlign=center` + `jc=center`, body cells keep `ind left/firstLine/right = 0` with `pPr` children in `PPR_ORDER`, and the processed table count and summary print are unchanged. For document-scoped behaviors it means all other stages produce byte-identical `document.xml` regions outside tables.

**Testing Approach**: Property-based testing is recommended for preservation because:
- It generates many table shapes (column counts, row counts, pre-existing grids, spans) automatically.
- It catches edge cases (empty grid, single column, ragged rows, `gridSpan`) that hand-written tests miss.
- It gives strong assurance that non-width behaviors and other stages are unchanged across the input domain.

**Test Plan**: Capture the current outputs for centering, header-cell centering, body-cell indentation clearing, and the table count/print on the unfixed code, then assert the fixed code reproduces them; and run a full-document formatting pass to confirm non-table regions are unchanged.

**Test Cases**:
1. **Table centering preservation**: For random tables, assert `tblPr/jc == center` after the fix, matching pre-fix behavior.
2. **Header-cell centering preservation**: Assert row-0 cells keep `vAlign=center` and `jc=center`.
3. **Body-cell indentation & ordering preservation**: Assert body-cell `pPr/ind` is zeroed and `pPr` children obey `PPR_ORDER`.
4. **Count/report preservation**: Assert every `w:tbl` is processed and the `Formatted N tables` summary is emitted with the correct N.
5. **Other-stage preservation**: Run the full `format_document_xmls` pipeline on a fixture and assert non-table content (paragraphs, drawings, `sectPr`/`pgSz`/`pgMar`, SDTs) is identical before/after the change.

### Unit Tests

- `compute_printable_width` returns `7937` for the real page setup and the documented defaults when `pgSz`/`pgMar` are missing or malformed.
- `column_ratios_from_grid` returns grid-derived proportions when a positive `tblGrid` exists and even proportions otherwise; column count honors `gridSpan`.
- `distribute_width` returns integer widths that sum exactly to `printable`, with the remainder on the last column; handles `n_cols = 1` and the optional `overrides` ratios.
- Table-level assertions: `tblW`, `tblLayout=fixed`, `tblGrid` rewrite, per-cell `tcW`, `tblHeader` on row 0, `tblBorders`, and `tblCellMar` are present with consistent values.

### Property-Based Tests

- Generate random tables (varied `n_cols`, `n_rows`, optional pre-existing grids, optional `gridSpan`) and assert Property 1 (total width == printable) and Property 2 (per-column widths sum to printable; proportions match grid when present, else even).
- Generate tables and assert Property 3 (row-0 `tblHeader`, `tblBorders`, `tblCellMar` present; valid OOXML ordering).
- Generate tables and assert Property 4 preservation invariants (centering, header-cell centering, indentation clearing, count/print) hold across many shapes, and that no code path branches on cell text or a specific column count.

### Integration Tests

- Full `format_document_xmls` run on a fixture `document.xml` containing several tables of different shapes: assert every table fits printable width and non-table content is unchanged.
- Cross-branch shape coverage: include table shapes representative of `laporan/iman`, `laporan/dwikhi`, and `laporan/faiz` (e.g., 2-, 4-, and 6-column tables) and assert uniform fit-to-printable treatment with no content-based special-casing.
- Confirm the emitted summary reports the correct number of tables and that `pgSz`/`pgMar` are untouched after the run.
