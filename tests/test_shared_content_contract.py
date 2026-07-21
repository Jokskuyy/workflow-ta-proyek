"""Contract tests for content distributed to every report branch."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "content" / "shared"


def _shared_text():
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(SHARED.rglob("*.md"))
    )


def _shared_results():
    return json.loads(
        (SHARED / "testing" / "results.json").read_text(encoding="utf-8")
    )


def test_shared_fragments_do_not_contain_team_identity():
    facts = json.loads((ROOT / "project_facts.json").read_text(encoding="utf-8"))
    text = _shared_text().casefold()

    for member in facts.get("team_members", []):
        name = str(member.get("name") or "").strip()
        nim = str(member.get("nim") or "").strip()
        if name:
            assert name.casefold() not in text
        if nim and nim.upper() != "TBD":
            assert nim.casefold() not in text


def test_shared_fragments_are_content_only_without_headings():
    for path in SHARED.rglob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            assert not line.lstrip().startswith("#"), (
                f"{path.relative_to(ROOT)} repeats a heading; headings belong "
                "to the branch draft"
            )


def test_blackbox_fragment_matches_structured_facts():
    result = _shared_results()["black_box_testing"]
    text = (SHARED / "testing" / "blackbox.md").read_text(encoding="utf-8")

    assert result["final_verification"]["passed_scenarios"] == result["total_scenarios"] == 24
    assert result["final_verification"]["failed_scenarios"] == []
    assert result["retest"]["scenario"] == "BB-20"
    assert result["retest"]["result"] == "passed"
    assert "24 dari 24" in text
    assert "skrip pengujian Unity" in text
    assert "dinyatakan lulus pada pengujian ulang" in text


def test_uat_fragment_matches_structured_scores():
    result = _shared_results()["user_acceptance_testing"]
    text = (SHARED / "testing" / "uat.md").read_text(encoding="utf-8")

    assert result["public_dashboard"]["score"] == 140
    assert result["admin_dashboard"]["score"] == 186
    assert result["combined"]["percentage"] == "81.50%"
    assert "140 dari skor maksimum 180" in text
    assert "186 dari skor maksimum 220" in text
    assert "326 dari skor maksimum 400" in text


def test_uat_revision_ids_are_complete_and_unique():
    text = (SHARED / "testing" / "uat-revisions.md").read_text(encoding="utf-8")
    status = _shared_results()["user_acceptance_testing"]["revision_status"]

    for number in range(1, 11):
        revision_id = f"UAT-R{number:02d}"
        assert text.count(revision_id) >= 1
        assert revision_id in status
    table_rows = [line for line in text.splitlines() if line.startswith("UAT-R")]
    assert len(table_rows) == 10
    assert len({line.split("|", 1)[0].strip() for line in table_rows}) == 10
    assert "UAT-R11" not in text
    assert "UAT-R11" not in status
