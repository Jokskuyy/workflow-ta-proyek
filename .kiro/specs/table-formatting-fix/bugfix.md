# Bugfix Requirements Document

## Introduction

The table-formatting logic in `skills/scripts/format_ta_proyek.py` (`format_all_tables()`) is brittle and hardcoded to a single specific table. It detects "Tabel 1.2 / Jadwal Kegiatan" by checking for exactly 6 columns and the literal word "Aktivitas" in the first cell, and only that one table receives column-width normalization. All other tables get no width normalization, so wide tables can overflow the printable page margins — inconsistent with images in the same script, which ARE scaled to the printable area. The detection is fragile: renaming "Aktivitas" or changing the column count silently breaks the only correctly-sized table.

Because `format_ta_proyek.py` is a SHARED script used across teammates' branches (`laporan/iman`, `laporan/dwikhi`, `laporan/faiz`), the fix must be general and content-agnostic. It must not special-case individual tables by their text or column count, so it works uniformly for any table any team member authors.

This bugfix replaces the content-specific special-casing with a general table formatter that fits total table width to the printable area, distributes column widths proportionally, repeats header rows, and applies consistent alignment and borders — for every table in the document.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a table has any layout other than exactly 6 columns with the literal word "Aktivitas" in its first cell THEN the system applies no `tblGrid`/`tcW` width normalization, allowing the table to overflow the printable page margins.

1.2 WHEN the target table's first cell is renamed away from containing "Aktivitas" OR its column count changes from 6 THEN the system silently stops normalizing that table's widths (`is_tabel_1_2` becomes false).

1.3 WHEN the target table IS detected THEN the system applies hardcoded magic numbers (first column `3500`, remaining columns `900` via a fixed `range(5)`) that do not adapt to actual column count or the printable page width.

1.4 WHEN any table is formatted THEN the system does not set header-row repeat (`tblHeader`), table borders, or cell padding, and does not enforce fit-to-window table width.

### Expected Behavior (Correct)

2.1 WHEN any table is formatted THEN the system SHALL normalize the total table width to fit within the printable area (page width minus left/right margins) so it does not overflow the page margins, regardless of column count or cell content.

2.2 WHEN any table is formatted THEN the system SHALL detect and format tables based on their structure (rows and columns) only, without special-casing any table by its cell text or specific column count.

2.3 WHEN a table's column widths are computed THEN the system SHALL distribute the printable width across columns proportionally (deriving proportions from the table's own grid where available, otherwise distributing evenly), using values computed from the actual column count and printable width rather than hardcoded magic numbers. The system SHALL support optional, non-hardcoded per-column width overrides.

2.4 WHEN a table is formatted THEN the system SHALL mark the first row as a repeating header row (`tblHeader`) and apply consistent alignment, borders, and cell padding to all tables.

### Unchanged Behavior (Regression Prevention)

3.1 WHEN any table is formatted THEN the system SHALL CONTINUE TO center the table horizontally (`tblPr/jc = center`).

3.2 WHEN a header row (first row) is formatted THEN the system SHALL CONTINUE TO center-align its cells both vertically and horizontally.

3.3 WHEN a body cell is formatted THEN the system SHALL CONTINUE TO clear paragraph indentation (`ind left/firstLine/right = 0`) and maintain valid OOXML child ordering via `sort_element_children(pPr, PPR_ORDER)`.

3.4 WHEN the formatter runs THEN the system SHALL CONTINUE TO process and count every `w:tbl` in `document.xml` and report the number of tables formatted.

3.5 WHEN other formatting stages run (numbering, images, captions, bibliography, headings) THEN the system SHALL CONTINUE TO behave exactly as before, since this fix is scoped to `format_all_tables()`.
