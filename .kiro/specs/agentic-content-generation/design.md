# Design — Agentic Content Generation

## Batas arsitektur

```text
AI/provider
    -> GenerationCandidate JSON
    -> guard fakta, sitasi, aturan, istilah, dan rujukan objek
    -> proposal + unified diff                 (default/suggest)
    -> pemeriksaan hash + atomic append        (hanya --apply)
    -> Tugas_Akhir_Draft.md
    -> run_alur() opsional / build_pipeline.py
```

`build_pipeline.py` dan `run_alur()` tidak mengimpor atau memanggil provider.
Dengan demikian kegagalan jaringan, biaya model, dan respons nondeterministik
tidak dapat memengaruhi build DOCX biasa.

## Komponen

1. `agentic_generation.py`
   - model request/candidate/result;
   - ekstraksi subbab dan bibliografi;
   - data minimisation untuk fakta;
   - validator mekanis dan provenance;
   - append murni yang mempertahankan baris lama;
   - orkestrasi `suggest`/`apply` dan concurrent-change guard.
2. `generation_providers.py`
   - `ResponseFileProvider` untuk handoff AI agent melalui JSON;
   - `HttpJsonProvider` untuk adaptor HTTP provider-neutral.
3. `generate_content.py`
   - deteksi branch;
   - `--prepare-out` untuk membuat request agentik;
   - output result dan unified diff;
   - satu-satunya flag penulisan: `--apply`.

## Kontrak kandidat

```json
{
  "section_id": "3.2.1",
  "markdown": "Body tanpa heading.",
  "fact_claims": [{"key": "a.b", "value": "nilai persis"}],
  "citations_used": ["(Nama 2024)"],
  "unverified_claims": [],
  "notes": []
}
```

Validator hanya dapat membuktikan provenance yang dideklarasikan dan aturan
mekanis. Karena klasifikasi semantik sebuah kalimat sebagai fakta masih dapat
salah, mode suggest + tinjauan manusia tetap menjadi default.

## Strategi preservasi

Apply tidak melakukan replacement. Kandidat body disisipkan sebelum heading
berikutnya pada direct body subbab target. Bila body kandidat yang sama sudah
ada, hasilnya `UNCHANGED`. Setelah provider selesai, hash draf dibandingkan
dengan hash request; perbedaan membatalkan apply sebelum atomic write.
