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

Unlike research theses (skripsi) which use a 5-chapter structure, project-based reports utilize a **4-chapter outline**:

* **BAB I PENDAHULUAN**
  * 1.1 Latar Belakang
  * 1.2 Identifikasi Masalah
  * 1.3 Batasan Masalah
  * 1.4 Tujuan dan Manfaat (with 1.4.1 Tujuan, 1.4.2 Manfaat)
  * 1.5 Jadwal Kegiatan
* **BAB II RANCANGAN PROYEK**
  * 2.1 Observasi
  * 2.2 Usulan Solusi
  * 2.3 Rancangan Proyek (User Interface, UML, ERD, etc.)
  * 2.4 Rencana Pengujian Proyek (Black Box, White Box)
* **BAB III IMPLEMENTASI PROYEK**
  * 3.1 Profil Mitra (Nama, Deskripsi, Hubungan)
  * 3.2 Metode Implementasi
  * 3.3 Metadata (Database description, Web Manifest, etc.)
  * 3.4 Laporan Implementasi Proyek (Logbook/activities list)
  * 3.5 Hasil Pengujian Proyek (UAT, Black Box results)
* **BAB IV PENUTUP**
  * 4.1 Kesimpulan
  * 4.2 Saran (Prospek keberlanjutan)

## Formatting Specifications

| Element | Specification |
|---------|---------------|
| **Paper Size** | A4 |
| **Margins** | Top = 3cm, Bottom = 3cm, Left = 4cm, Right = 3cm |
| **Font Name** | Times New Roman (all text, including styles, headers, footers, tables, and captions) |
| **Font Size** | Body (12pt), Headings (12pt Bold), Chapter Titles (14pt Bold Centered), Abstracts (11pt) |
| **Line Spacing** | Body & Headings (1.5), Captions & Bibliography (1.0) |
| **Indentations** | Body paragraphs (1.0cm first-line indent), Bibliography (1.0cm hanging indent) |
| **Table Captions** | Placed **above** the table, centered, e.g., **Tabel 1.1** Description (no trailing dot after number) |
| **Figure Captions** | Placed **below** the figure, centered, e.g., **Gambar 2.3** Description (no trailing dot after number) |
| **Front Matter Pages** | Lower Roman numerals (`i, ii, iii...`) centered at the bottom |
| **Body Pages** | Arabic numerals (`1, 2, 3...`) centered at the bottom, restarting at page 1 for Chapter 1 |
| **TOC & bibliography** | Center-aligned title, unnumbered Heading1, fonts forced to Times New Roman |
| **Page Splits** | Table of Contents (Daftar Isi), Table of Figures (Daftar Gambar), Table of Tables (Daftar Tabel) must be on separate pages |
| **Cover Page** | Cover page must be on its own page and separated from the rest of the document |
| **Table of Appendices** | Table of Appendices (Daftar Lampiran) must be placed on its own page after the Table of Tables (Daftar Tabel). Appendices (LAMPIRAN 1-4) must be excluded from the main Table of Contents (Daftar Isi) by using custom styling without outline levels. |
| **Images & Figures** | Must preserve their original aspect ratio and must not be stretched or distorted. Sizing must adjust dynamically based on actual image dimensions. |

## Handling Discrepancies & Ambiguities

1. **JANGAN BERASUMSI (DO NOT ASSUME)**: If there are any ambiguities, discrepancies, or missing information in the report content (e.g., mismatched figures, placeholder references like `Gambar 2.x`, missing table/figure captions, or formatting conflicts), the formatting assistant MUST NOT assume a solution or auto-generate content without explicit user approval.
2. **Interactive Clarification**: Present all detected issues or discrepancies to the user with their surrounding context, and ask the user to verify or choose how to proceed before making any changes.
3. **No Silent Auto-generation**: Any automatic generation of captions or content based on context must be presented as a proposal to the user first.

