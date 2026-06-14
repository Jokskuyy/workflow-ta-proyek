---
name: write-ta-proyek
description: "Draft, verify, and refine UPN Veteran Jakarta project-based final year reports (Tugas Akhir Proyek) using interactive guidelines, strict terminology checks, and automated citation mapping."
---

# Laporan Tugas Akhir Proyek Writing & Content Guide

## Overview

Writing skill to guide users through drafting, verifying, and citing UPN Veteran Jakarta project-based reports ("Tugas Akhir Proyek").

## Triggers

Use this skill when:
- Writing or drafting content for project-based final year report chapters.
- Clarifying guidelines or content gaps for a thesis draft.
- Adding theoretical definitions and academic citations.
- Verifying the consistency of technical terms throughout a report draft.

## Core Writing Rules

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

## Drafting & File Outputs

The writing process uses the following files in the workspace parent directory (`../`):
1. **Master Draft (`laporan_draft.md`)**: The single source of truth containing all written chapters, sub-chapters, and placeholders.
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


