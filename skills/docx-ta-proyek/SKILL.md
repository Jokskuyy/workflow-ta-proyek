---
name: docx-ta-proyek
description: "Format project-based final year reports (Tugas Akhir Proyek) for UPN Veteran Jakarta (FIK 2025) in .docx format. Use when formatting final year project reports, outline formatting, margins, font sizing, page numbering, table/figure captions, or cleaning bibliography entries."
---

# Laporan Tugas Akhir Proyek Formatting (UPN Veteran Jakarta FIK 2025)

## Overview

Advanced formatting automation for UPN Veteran Jakarta project-based final year reports ("Tugas Akhir Proyek"), featuring a 4-chapter outline and academic style rules.

## Quick Start

1. **Unpack** the `.docx` document:
   ```bash
   python skills/scripts/unpack.py input.docx unpacked_dir
   ```
2. **Inject Numbering Presets**:
   ```bash
   python skills/scripts/add_numbering_preset.py unpacked_dir
   ```
3. **Format Layout & Styling**:
   ```bash
   python skills/scripts/format_ta_proyek.py unpacked_dir
   ```
4. **Pack** the document back:
   ```bash
   python skills/scripts/pack.py unpacked_dir output.docx
   ```

## Chapter Outline (Tugas Akhir Proyek)

Berbeda dari skripsi (5 bab), laporan berbasis proyek memakai **kerangka 4 bab**. Kerangka lengkap & terkini ada pada sumber kanonik bersama: **`../references/outline-4bab.md`**.

## Formatting Specifications

Spesifikasi format lengkap (margin, font, caption, page split, Daftar Lampiran, gambar) ada pada sumber kanonik bersama: **`../references/format-spec-upnvj.md`**.

## Handling Discrepancies & Ambiguities

1. **JANGAN BERASUMSI (DO NOT ASSUME)**: If there are any ambiguities, discrepancies, or missing information in the report content (e.g., mismatched figures, placeholder references like `Gambar 2.x`, missing table/figure captions, or formatting conflicts), the formatting assistant MUST NOT assume a solution or auto-generate content without explicit user approval.
2. **Interactive Clarification**: Present all detected issues or discrepancies to the user with their surrounding context, and ask the user to verify or choose how to proceed before making any changes.
3. **No Silent Auto-generation**: Any automatic generation of captions or content based on context must be presented as a proposal to the user first.

