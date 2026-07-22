"""Checks for canonical role attribution and terminology decisions."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_facts_json_is_valid_and_role_scope_is_current():
    facts = json.loads((ROOT / "project_facts.json").read_text(encoding="utf-8"))
    role = next(item for item in facts["team_members"] if item["name"] == "Dwikhi Deandra Purnianto")
    assert any("RLS" in item for item in role["focus"])
    assert any("audit_logs" in item for item in role["focus"])
    ownership = facts["database_schema"]["integration_ownership"]
    assert "Iman" in ownership
    assert "trigger audit database tidak diklaim" in ownership


def test_draft_does_not_claim_production_trigger_or_exclusive_tool_ownership():
    draft = (ROOT / "Tugas_Akhir_Draft.md").read_text(encoding="utf-8")
    assert "trigger audit database tidak diklaim" in draft
    assert "DatabaseSyncChecker` dikembangkan oleh Faiz" in draft
    assert "kebutuhan kebijakan RLS" in draft
    assert "struktur tabel `audit_logs`" in draft
    assert "kontrak runtime" not in draft


def test_registry_keeps_acronyms_regular_and_full_terms_italic():
    registry = json.loads((ROOT / "term_registry.json").read_text(encoding="utf-8"))
    assert "API" in registry["formatting"]["regular_acronyms"]
    assert "SQL" in registry["formatting"]["regular_acronyms"]
    assert "RLS" in registry["formatting"]["regular_acronyms"]
    assert "Full Stack Web Developer" in registry["formatting"]["italic_full_terms"]
