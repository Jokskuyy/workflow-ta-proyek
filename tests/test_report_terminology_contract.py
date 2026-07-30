"""Regression guards for human-readable terminology in Iman's report."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "Tugas_Akhir_Draft.md"


def _indonesian_report_text() -> str:
    paths = [
        DRAFT,
        ROOT / "content/shared/bab1/latar-belakang-umum.md",
        ROOT / "content/shared/bab2/sumber-data-dan-batas-observasi.md",
        ROOT / "content/shared/bab2/analisis-kebutuhan-dan-sistem-berjalan.md",
        ROOT / "content/shared/testing/blackbox.md",
        ROOT / "content/shared/testing/uat.md",
        ROOT / "content/shared/testing/uat-revisions.md",
        ROOT / "content/roles/iman/uat-revisions.md",
        ROOT / "content/shared/testing/appendix-instruments.md",
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def _without_code_and_bibliography(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return text.split("# DAFTAR PUSTAKA", 1)[0]


def test_indonesian_report_uses_agreed_canonical_terms():
    text = _without_code_and_bibliography(_indonesian_report_text())
    forbidden = {
        "Dasbor Publik",
        "Public Dashboard",
        "Admin Panel",
        "basis data",
        "perangkat bergerak",
        "perangkat seluler",
        "peramban",
        "penyimpanan sementara",
        "nilai rahasia",
        "pemberitahuan penyelesaian navigasi",
        "kode objek",
        "artefak WebGL",
        "proses kompilasi",
    }
    found = sorted(term for term in forbidden if term.casefold() in text.casefold())
    assert not found, f"Istilah nonkanonik masih ditemukan: {found}"

    registry = json.loads((ROOT / "term_registry.json").read_text(encoding="utf-8"))
    canonical = registry["istilah_teknis"]
    assert canonical["public dashboard"] == "Dashboard Publik"
    assert canonical["admin panel"] == "Panel Admin"
    assert canonical["mobile device"] == "smartphone"
    assert canonical["stakeholder"] == "pemangku kepentingan"


def test_foreign_abbreviation_introductions_use_italic_long_forms():
    draft = DRAFT.read_text(encoding="utf-8")
    required = {
        "*Unified Modeling Language* (UML)",
        "*Row Level Security* (RLS)",
        "*Entity Relationship Diagram* (ERD)",
        "*User Acceptance Test* (UAT)",
    }
    missing = sorted(value for value in required if value not in draft)
    assert not missing, f"Format pengenalan singkatan belum sesuai: {missing}"


def test_english_abstract_remains_english():
    front_matter = json.loads(
        (ROOT / "content/roles/iman/front-matter.json").read_text(encoding="utf-8")
    )
    abstract = front_matter["abstract_en"]["body"]
    assert "Public Dashboard and Admin Panel" in abstract
    assert "Performance score of 86 on mobile and 99 on desktop" in abstract
