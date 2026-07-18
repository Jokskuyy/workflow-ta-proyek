"""Regression tests for guarded, optional agentic Markdown generation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from alur_penulisan.agentic_generation import (  # noqa: E402
    CandidateFactClaim,
    GenerationCandidate,
    GenerationStatus,
    run_agentic_generation,
)
from alur_penulisan.fact_verifier import FactStore  # noqa: E402
from alur_penulisan.generation_providers import ResponseFileProvider  # noqa: E402


DRAFT = """# BAB III IMPLEMENTASI PROYEK

## 3.2 Metode Implementasi

### 3.2.1 Implementasi Back-end

Konten manual yang harus tetap utuh.

### 3.2.2 Implementasi Front-end

Isi front-end.

# DAFTAR PUSTAKA

Aliyah, A., Hartono, N., & Muin, A. A. (2024). Penggunaan User Acceptance Testing.

---
"""


class StaticProvider:
    def __init__(self, candidate: GenerationCandidate) -> None:
        self.candidate = candidate
        self.calls = 0

    def generate(self, request):
        self.calls += 1
        return self.candidate


class WriteSpy:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def __call__(self, path: str, content: str) -> None:
        self.calls.append((path, content))


def _candidate(markdown: str = "Usulan tambahan yang sudah ditinjau.") -> GenerationCandidate:
    return GenerationCandidate(section_id="3.2.1", markdown=markdown)


def _run(
    provider,
    *,
    apply=False,
    read=lambda _path: DRAFT,
    write=None,
    facts=None,
    fact_keys=(),
):
    write = write or WriteSpy()
    facts = facts or FactStore.from_mapping({})
    return run_agentic_generation(
        provider,
        draft_path="draft.md",
        section_id="3.2.1",
        instruction="Lengkapi pembahasan.",
        active_branch="laporan/iman",
        apply=apply,
        fact_keys=fact_keys,
        read=read,
        write=write,
        load_facts=lambda _path: facts,
        term_registry_path="missing-term-registry.json",
    )


def test_suggest_is_default_and_never_writes_markdown():
    write = WriteSpy()
    result = _run(StaticProvider(_candidate()), write=write)

    assert result.status is GenerationStatus.SUGGESTED
    assert result.wrote_draft is False
    assert write.calls == []
    assert result.diff
    assert "Usulan tambahan" in result.diff


def test_apply_appends_only_to_target_and_preserves_manual_content():
    write = WriteSpy()
    result = _run(StaticProvider(_candidate()), apply=True, write=write)

    assert result.status is GenerationStatus.APPLIED
    assert result.wrote_draft is True
    assert len(write.calls) == 1
    written = write.calls[0][1]
    assert "Konten manual yang harus tetap utuh." in written
    assert "Isi front-end." in written
    assert written.count("Usulan tambahan yang sudah ditinjau.") == 1
    assert written.index("Usulan tambahan") < written.index("### 3.2.2")


def test_apply_is_idempotent_when_exact_candidate_already_exists():
    existing = DRAFT.replace(
        "Konten manual yang harus tetap utuh.",
        "Konten manual yang harus tetap utuh.\n\nUsulan tambahan yang sudah ditinjau.",
    )
    write = WriteSpy()
    result = _run(
        StaticProvider(_candidate()),
        apply=True,
        read=lambda _path: existing,
        write=write,
    )

    assert result.status is GenerationStatus.UNCHANGED
    assert result.wrote_draft is False
    assert write.calls == []


def test_apply_aborts_if_human_edits_draft_during_provider_call():
    reads = iter([DRAFT, DRAFT.replace("Isi front-end.", "Edit baru manusia.")])
    write = WriteSpy()
    result = _run(
        StaticProvider(_candidate()),
        apply=True,
        read=lambda _path: next(reads),
        write=write,
    )

    assert result.status is GenerationStatus.REJECTED
    assert any(issue.code == "draft_changed_during_generation" for issue in result.issues)
    assert write.calls == []


def test_unknown_branch_is_held_before_read_or_provider_call():
    provider = StaticProvider(_candidate())
    reads: list[str] = []
    write = WriteSpy()
    result = run_agentic_generation(
        provider,
        draft_path="draft.md",
        section_id="3.2.1",
        instruction="Lengkapi.",
        active_branch="master",
        read=lambda path: reads.append(path) or DRAFT,
        write=write,
    )

    assert result.status is GenerationStatus.HELD
    assert provider.calls == 0
    assert reads == []
    assert write.calls == []


def test_branch_with_matching_last_segment_cannot_spoof_report_scope():
    provider = StaticProvider(_candidate())
    result = run_agentic_generation(
        provider,
        draft_path="draft.md",
        section_id="3.2.1",
        instruction="Lengkapi.",
        active_branch="feature/iman",
        read=lambda _path: DRAFT,
    )

    assert result.status is GenerationStatus.HELD
    assert provider.calls == 0


def test_bullet_and_heading_candidates_are_rejected():
    candidate = _candidate("#### Heading liar\n\n- bullet terlarang")
    write = WriteSpy()
    result = _run(StaticProvider(candidate), apply=True, write=write)

    assert result.status is GenerationStatus.REJECTED
    assert {issue.code for issue in result.issues} >= {
        "heading_forbidden",
        "bullet_forbidden",
    }
    assert write.calls == []


def test_project_fact_must_match_fact_store_exactly():
    facts = FactStore.from_mapping(
        {"testing_status": {"black_box_testing": {"completed": True}}}
    )
    candidate = GenerationCandidate(
        section_id="3.2.1",
        markdown="Status pengujian yang dinyatakan adalah false.",
        fact_claims=(
            CandidateFactClaim(
                key="testing_status.black_box_testing.completed",
                value="false",
            ),
        ),
    )
    result = _run(
        StaticProvider(candidate),
        facts=facts,
        fact_keys=("testing_status.black_box_testing.completed",),
    )

    assert result.status is GenerationStatus.REJECTED
    assert any(issue.code == "fact_value_mismatch" for issue in result.issues)


def test_exact_project_fact_requires_explicit_fact_selection():
    key = "testing_status.black_box_testing.completed"
    facts = FactStore.from_mapping(
        {"testing_status": {"black_box_testing": {"completed": True}}}
    )
    candidate = GenerationCandidate(
        section_id="3.2.1",
        markdown="Status completed yang digunakan adalah true.",
        fact_claims=(CandidateFactClaim(key=key, value="true"),),
    )

    rejected = _run(StaticProvider(candidate), facts=facts)
    accepted = _run(StaticProvider(candidate), facts=facts, fact_keys=(key,))

    assert rejected.status is GenerationStatus.REJECTED
    assert any(
        issue.code == "fact_not_authorized_for_request" for issue in rejected.issues
    )
    assert accepted.status is GenerationStatus.SUGGESTED


def test_missing_fact_is_allowed_only_as_declared_tbd():
    candidate = GenerationCandidate(
        section_id="3.2.1",
        markdown="Jumlah responden adalah [TBD: jumlah responden UAT].",
        fact_claims=(
            CandidateFactClaim(
                key="testing_status.user_acceptance_test_uat.respondent_count",
                value="[TBD: jumlah responden UAT]",
            ),
        ),
    )
    result = _run(StaticProvider(candidate))

    assert result.status is GenerationStatus.SUGGESTED
    assert not [issue for issue in result.issues if issue.severity.value == "error"]


def test_citation_must_exist_in_bibliography_and_match_declaration():
    valid = GenerationCandidate(
        section_id="3.2.1",
        markdown="UAT mendukung evaluasi penerimaan pengguna (Aliyah et al. 2024).",
        citations_used=("(Aliyah et al. 2024)",),
    )
    invalid = GenerationCandidate(
        section_id="3.2.1",
        markdown="Klaim palsu (TidakAda 2099).",
        citations_used=("(TidakAda 2099)",),
    )

    assert _run(StaticProvider(valid)).status is GenerationStatus.SUGGESTED
    rejected = _run(StaticProvider(invalid))
    assert rejected.status is GenerationStatus.REJECTED
    assert any(issue.code == "citation_not_in_bibliography" for issue in rejected.issues)


def test_unverified_claim_requires_marker_and_metadata():
    candidate = GenerationCandidate(
        section_id="3.2.1",
        markdown="Teknologi ini selalu meningkatkan kinerja. [BUTUH SITASI]",
        unverified_claims=("Klaim peningkatan kinerja belum memiliki sumber.",),
    )
    result = _run(StaticProvider(candidate))

    assert result.status is GenerationStatus.SUGGESTED
    assert any(issue.code == "unverified_claim" for issue in result.issues)


def test_object_reference_must_be_mid_sentence_existing_and_same_chapter():
    draft_with_figure = DRAFT.replace(
        "Konten manual yang harus tetap utuh.",
        "Konten manual yang harus tetap utuh.\n\nGambar 3.1 Arsitektur implementasi.",
    )
    valid = _candidate("Alur komponen dirangkum pada Gambar 3.1.")
    dangling = _candidate("Alur komponen dirangkum pada Gambar 3.9.")
    sentence_start = _candidate("Gambar 3.1 menunjukkan alur komponen.")

    assert _run(
        StaticProvider(valid), read=lambda _path: draft_with_figure
    ).status is GenerationStatus.SUGGESTED

    dangling_result = _run(
        StaticProvider(dangling), read=lambda _path: draft_with_figure
    )
    assert dangling_result.status is GenerationStatus.REJECTED
    assert any(
        issue.code == "dangling_object_reference" for issue in dangling_result.issues
    )

    start_result = _run(
        StaticProvider(sentence_start), read=lambda _path: draft_with_figure
    )
    assert start_result.status is GenerationStatus.REJECTED
    assert any(
        issue.code == "invalid_object_reference_position"
        for issue in start_result.issues
    )


def test_response_file_provider_accepts_agent_neutral_candidate(tmp_path):
    response = tmp_path / "candidate.json"
    response.write_text(
        json.dumps({"candidate": _candidate().to_mapping()}),
        encoding="utf-8",
    )
    result = _run(ResponseFileProvider(str(response)))

    assert result.status is GenerationStatus.SUGGESTED
    assert result.candidate is not None
    assert result.candidate.section_id == "3.2.1"


def test_cli_requires_apply_before_markdown_changes(tmp_path):
    draft = tmp_path / "draft.md"
    facts = tmp_path / "facts.json"
    terms = tmp_path / "terms.json"
    response = tmp_path / "candidate.json"
    draft.write_text(DRAFT, encoding="utf-8")
    facts.write_text("{}\n", encoding="utf-8")
    terms.write_text('{"istilah_teknis": {}}\n', encoding="utf-8")
    response.write_text(json.dumps(_candidate().to_mapping()), encoding="utf-8")

    command = [
        sys.executable,
        str(SCRIPTS / "generate_content.py"),
        "--draft",
        str(draft),
        "--facts",
        str(facts),
        "--term-registry",
        str(terms),
        "--branch",
        "laporan/iman",
        "--section",
        "3.2.1",
        "--response-file",
        str(response),
    ]
    suggested = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)

    assert '"status": "suggested"' in suggested.stdout
    assert draft.read_text(encoding="utf-8") == DRAFT

    applied = subprocess.run(
        command + ["--apply"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    assert '"status": "applied"' in applied.stdout
    assert "Usulan tambahan yang sudah ditinjau." in draft.read_text(encoding="utf-8")
