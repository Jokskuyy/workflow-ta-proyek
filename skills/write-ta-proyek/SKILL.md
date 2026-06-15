---
name: write-ta-proyek
description: "Draft, verify, refine, and format UPN Veteran Jakarta project-based final year reports (Tugas Akhir Proyek) in Markdown and .docx formats, including content auditing, citations, and automated styling."
---

# Laporan Tugas Akhir Proyek Writing, Content & Formatting Guide

## Overview

A unified writing and formatting skill to guide users through drafting, content verification, citation tracking, and formatting automation for UPN Veteran Jakarta project-based reports ("Tugas Akhir Proyek").

## Triggers

Use this skill when:
- Writing or drafting content for project-based final year report chapters.
- Clarifying guidelines, templates, or content gaps for a thesis draft.
- Adding theoretical definitions and academic citations.
- Verifying the consistency of technical terms throughout a report draft.
- Formatting `.docx` final year reports according to UPNVJ FIK 2025 guidelines.

## Quick Start (Formatting Automation)

To automate the formatting of your `.docx` document:

1. **Unpack** the `.docx` document:
   ```bash
   python write-ta-proyek/scripts/unpack.py input.docx unpacked_dir
   ```
2. **Inject Numbering Presets**:
   ```bash
   python write-ta-proyek/scripts/add_numbering_preset.py unpacked_dir
   ```
3. **Format Layout & Styling**:
   ```bash
   python write-ta-proyek/scripts/format_ta_proyek.py unpacked_dir
   ```
4. **Pack** the document back:
   ```bash
   python write-ta-proyek/scripts/pack.py unpacked_dir output.docx
   ```

## Core Writing & Content Rules

1. **Theoretical Sub-chapter Definition & Citation**:
   - Any theoretical sub-chapter (e.g., UAT, black box testing, ERD, Unity) MUST start with a clear, academic definition paragraph.
   - Every definition paragraph MUST contain at least one formal citation.

2. **PRD & Project Details Auditing**:
   - Compare user-provided PRD, requirements, or logbook records against the document draft.
   - If there is any missing information or inconsistency, the agent MUST NOT make assumptions. The agent MUST warn the user, point out the discrepancy, and propose a specific correction.

3. **Visual Recommendations & Figure Integration**:
   - When introducing complex workflows, database designs, or architectures, identify if a figure/diagram would improve clarity.
   - Propose the inclusion of a figure, either by searching the web for a verified illustration (providing URL source) or suggesting to generate/draw it.

4. **Strict Terminology Consistency**:
   - Enforce consistency for all technical terms throughout the document.
   - *Example*: If "user interface" is used first, do not switch to "antarmuka". If "database" is used, do not switch to "basis data". Maintain a consistent terminology registry for the session.

5. **Citation Sourcing Pipeline**:
   - **Local Search**: First, scan the local `journal/` directory in the parent folder (`../journal/`) for relevant scientific papers or references.
   - **Web Search**: If no suitable local paper exists, search the web (prioritize Google Scholar or verified journals) for authentic scientific sources. Include the authors, year, title, journal name, and direct source link.

6. **Interactive Follow-up & Writing Logic**:
   - Always present drafts incrementally (sub-chapter by sub-chapter).
   - Ask clarifying follow-up questions if there are multiple logical structures or ambiguities in project details.
   - Ensure you ask the user if there are other aspects (existing or missing) in `/write-ta-proyek` to update.

7. **No Pointer Symbols (Bullet Points)**:
   - Markdown bullet points (e.g., `-`, `*`, `+`) MUST NOT be used for listing items in the draft report.
   - All lists must use numerical or alphabetical indicators. The hierarchy should follow:
     - Level 1: Numbers with dot (e.g., `1.`, `2.`)
     - Level 2: Letters with dot (e.g., `a.`, `b.`)
     - Level 3: Numbers with closing parenthesis (e.g., `1)`, `2)`)
     - Level 4: Letters with closing parenthesis (e.g., `a)`, `b)`)

8. **Figure and Table Narrative Mentions**:
   - Do NOT mention a figure or table as the first word of a paragraph or sentence (e.g., "Gambar 2.1 menunjukkan bahwa...", "Tabel 3.1 berisi...").
   - Instead, mention the figure or table in the middle of a sentence (e.g., "Like as shown in Gambar 2.1, ...", "Peran pengembang secara rinci dapat dilihat pada Tabel 1.1.").

9. **Appendices (Lampiran) Formatting**:
   - Penomoran lampiran wajib menggunakan format angka Arab kapital dengan titik: **LAMPIRAN 1.**, **LAMPIRAN 2.**, dst.
   - Setiap lampiran wajib diawali pada halaman baru terpisah (Page Isolation/Page Split menggunakan `---` di Markdown) untuk meminimalkan kegagalan pemformatan dokumen.
   - Daftar lampiran wajib tercantum pada bagian awal dokumen setelah Daftar Tabel.
   - Daftar lampiran harus terisolasi terpisah dari Daftar Isi, di mana lampiran individu (LAMPIRAN 1-4) dilarang muncul di Daftar Isi dengan menerapkan gaya paragraf kustom tanpa outline level.
   - Lampiran wajib menyertakan minimal:
     * LAMPIRAN 1. Surat Pernyataan Keaslian
     * LAMPIRAN 2. Surat Keterangan Implementasi Proyek dari Mitra
     * LAMPIRAN 3. Kode Sumber Utama (Source Code)
     * LAMPIRAN 4. Panduan Pengguna (User Manual) (disiapkan sebagai placeholder jika belum selesai)

10. **Fact Verification & Registry Audit**:
    - The agent MUST verify the existence of `project_facts.json` before drafting or modifying any report chapters.
    - Under NO circumstances should the agent invent, guess, or copy empirical testing figures (like UAT percentages, participant counts, lighthouse load times, or specific database row counts) from reference materials (like senior theses).
    - Check the `testing_status` within `project_facts.json`. If a testing stage (e.g. UAT or Black Box) is marked as `completed: false` or has `null` values, the agent MUST write clear placeholders (such as `[TBD: Jumlah Responden]` or `[TBD: Skor UAT]`) instead of realistic numbers.
    - If `completed: true`, the agent must use the exact numbers stored in `project_facts.json` without any alterations.
    - Verify that no details from `Tugas Akhir_Abimanyu Damarjati_2110511110.pdf` are used as facts for the user's project.




## Formatting Specifications (UPNVJ FIK 2025)

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

## Handling Discrepancies & Ambiguities

1. **JANGAN BERASUMSI (DO NOT ASSUME)**: If there are any ambiguities, discrepancies, or missing information in the report content (e.g., mismatched figures, placeholder references like `Gambar 2.x`, missing table/figure captions, or formatting conflicts), the formatting assistant MUST NOT assume a solution or auto-generate content without explicit user approval.
2. **Interactive Clarification**: Present all detected issues or discrepancies to the user with their surrounding context, and ask the user to verify or choose how to proceed before making any changes.
3. **No Silent Auto-generation**: Any automatic generation of captions or content based on context must be presented as a proposal to the user first.

## 4-Chapter Report Outline (Tugas Akhir Proyek UPNVJ FIK 2025)

The report draft MUST follow the 4-chapter project outline structure. Below is the detailed chapter and subchapter layout mapping UPNVJ FIK 2025 guidelines and senior thesis styles:

### BAB I PENDAHULUAN
* **1.1 Latar Belakang**: Explains smart campus context, spatial navigation difficulties, collaborative roles, and the author's full-stack development/system integration focus.
* **1.2 Identifikasi Masalah**: Enumerated list of problems (using numbered/lettered lists).
* **1.3 Batasan Masalah**: Ruiz-scoped limits (A4 size, Pondok Labu campus, full-stack dev limits, Supabase auth, RLS, WebGL bridge limits).
* **1.4 Tujuan dan Manfaat**
  * **1.4.1 Tujuan**: Expected system goals.
  * **1.4.2 Manfaat**: Practical gains for users, managers, and the institution.
* **1.5 Jadwal Kegiatan**: Project schedule (using Gantt chart or table format).

### BAB II RANCANGAN PROYEK
* **2.1 Observasi**: Details on running systems, surveys/questionnaires, and domain expert interviews.
* **2.2 Usulan Solusi**: Concept diagram and technical architecture.
  * **2.2.1 Identifikasi Kebutuhan Fungsional**: Grouped by User, Admin, and Integration/API requirements.
  * **2.2.2 Identifikasi Kebutuhan Teknis**: Stacks (React SPA, Express API, Supabase DB, Umami Analytics, Unity WebGL).
* **2.3 Rancangan Proyek**
  * **2.3.1 Rencana Pengembangan**: Prototyping phases.
  * **2.3.2 Perancangan Information Architecture (IA)**: App hierarchy.
  * **2.3.3 Perancangan Unified Modelling Language (UML)**: Use Case, Activity, and Sequence diagrams.
  * **2.3.4 Perancangan Sistem Spesifik**: System configurations (e.g., scheduled notifications, database trigger designs, RLS, reverse proxies).
  * **2.3.5 Perancangan Entity Relationship Diagram (ERD)**: Data schema model.
  * **2.3.6 Perancangan Antarmuka**: Visual layout mocks for Public Dashboard and Admin Panel.
* **2.4 Rencana Pengujian Proyek**: Test strategies (Black Box and UAT design).

### BAB III IMPLEMENTASI PROYEK
* **3.1 Profil Mitra**
  * **3.1.1 Nama Organisasi/Lembaga Mitra**
  * **3.1.2 Deskripsi Mitra**
  * **3.1.3 Hubungan Mitra dengan Proyek**
* **3.2 Metode Implementasi**
  * **3.2.1 Implementasi Back-end**: Express.js serverless functions, database schema implementation, SQL code snippets.
  * **3.2.2 Implementasi Front-end**: React SPA component details, routing, WebGL communications.
* **3.3 Metadata**
  * **3.3.1 Basis Data**: Schema tables and keys mapped to Unity.
  * **3.3.2 Deskripsi Jenis Notifikasi / Proxy Analytics**: Reverse proxy settings and self-hosted tracker collect configurations.
  * **3.3.3 Web Manifest / Web Assets**: Assets configurations.
* **3.4 Laporan Implementasi Proyek**
  * **3.4.1 Logbook Implementasi Proyek**: Logbook table with activity lists and validation.
  * **3.4.2 Hasil Implementasi Back-end**: API endpoint returns and implementation code.
  * **3.4.3 Hasil Implementasi Front-end**: Mocks, screenshots, and visual page outputs.
* **3.5 Hasil Pengujian Proyek**
  * **3.5.1 Black Box Testing**: Sceanrios execution table.
  * **3.5.2 Lighthouse Testing / Performance testing**: Performance and SEO benchmark metrics.
  * **3.5.3 User Acceptance Test (UAT)**: Likert questionnaire details and overall satisfaction rating computations.
  * **3.5.4 Implementasi Hasil User Acceptance Test (UAT)**: Post-test system improvements.

### BAB IV PENUTUP
* **4.1 Kesimpulan**: Concise summary of results.
* **4.2 Saran**: Sustainability and future roadmap recommendations.

## Drafting & File Outputs

The writing process uses the following files in the workspace parent directory (`../`):
1. **Master Draft (`Tugas_Akhir_Draft.md`)**: The single source of truth containing all written chapters, sub-chapters, and placeholders.
   - **Why Markdown (.md) is used**: Text-based markdown is highly optimized for LLMs to read, edit, and track changes securely without causing file corruption. Directly editing `.docx` files is prone to XML/styling corruption.
   - **Markdown-to-Docx Workflow**: Once the draft in `Tugas_Akhir_Draft.md` is approved, the text is imported or pasted into `Tugas_Akhir.docx`, and the formatting automation pipeline (unpacking, styling via python scripts, and repacking) is executed to compile `Tugas_Akhir_Formatted.docx`.
2. **Terminology Registry (`term_registry.json`)**: Auto-generated dictionary of technical terms (e.g. `{"user interface": "user interface"}`) to enforce document-wide consistency.
3. **Citations Tracker (`citations_to_download.md`)**: List of references generated during web searches that need their corresponding PDF files placed in the `journal/` directory.


## Group Project Settings (UPNVJ FIK 2025)

### Team Members & Roles
- **Muhammad Iman Nugraha** (NIM 2210511129)
  - **Role**: *Peran 1: Full Stack Web Developer & System Integrator*
  - **Focus Areas**: React Frontend, Serverless API, Supabase Auth, Umami Analytics Proxy, System Integration, Vitest.
- **Muammar Faiz Khairul Anam**
  - **Role**: *Peran 2: 3D Simulator & Engine Developer*
  - **Focus Areas**: Unity WebGL Engine, NavMesh pathfinding, Catmull-Rom Centripetal curve, Building Culling, Pointer Lock, Virtual mobile joystick, Editor tools (WebGL Settings Optimizer, Database Sync Checker).
- **Muhammad Dwikhi Deandra Purnianto**
  - **Role**: *Peran 3: 3D Asset Designer & Database/Asset Manager*
  - **Focus Areas**: 3D modeling and layout directly in Unity Editor (no Blender), PostgreSQL database schema design in Supabase Cloud, RLS policies, audit logs triggers, data mapping/integrity (`unity_object_name` bridge).

### Technical & Environment Constraints
- **3D Modeling & Layout**: Executed directly in **Unity Editor** instead of external software like Blender.
- **Database**: PostgreSQL hosted on **Supabase Cloud**, utilizing database triggers for `audit_logs` and Row Level Security (RLS) for data protection.
- **Analytics**: **Umami Analytics** self-hosted (port 3000) with Express.js proxy server (port 3001).
