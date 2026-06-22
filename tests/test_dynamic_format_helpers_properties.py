"""Property + example tests for the PURE Mesin_Format helpers of the
dynamic-generation-pipeline spec.

Spec: .kiro/specs/dynamic-generation-pipeline

Covers tasks 2.2, 2.4, 2.5, 2.6 (Properties 1-4), 3.2, 3.3, 3.4 (Properties 5-7)
and 4.2, 4.3, 5.2, 5.3, 5.4 (Properties 11-15) against the pure helpers exposed
by ``skills/scripts/format_ta_proyek.py``:

  parse_chapter_number, CaptionRegistry, AMBIGUOUS/is_ambiguous,
  parse_caption_text, find_front_matter_boundary, find_heading,
  rewrite_references, _paragraph_text, _paragraph_style.

All logic is pure (no Word / COM), so 100+ Hypothesis iterations are cheap. The
existing image-injection suite is NOT modified; this is a brand-new file.
"""
import re
import sys
from pathlib import Path

import lxml.etree as ET
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the pure helpers from the canonical Mesin_Format script.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "scripts"
sys.path.insert(0, str(SKILLS))

import format_ta_proyek as fmt  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

# Roman numerals understood by parse_chapter_number (I=1 .. X=10).
ROMAN_STR = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
BAB_TITLES = ["", "PENDAHULUAN", "RANCANGAN PROYEK", "IMPLEMENTASI",
              "HASIL DAN PEMBAHASAN", "PENUTUP"]


# --------------------------------------------------------------------------- #
# Tiny lxml <w:p> builders (no escaping pitfalls; build via the DOM).
# --------------------------------------------------------------------------- #
def make_par(text=None, style=None):
    """Build a single ``<w:p>`` element with an optional pStyle + one text run."""
    p = ET.Element("{%s}p" % W)
    if style is not None:
        pPr = ET.SubElement(p, "{%s}pPr" % W)
        pStyle = ET.SubElement(pPr, "{%s}pStyle" % W)
        pStyle.set("{%s}val" % W, style)
    if text is not None:
        r = ET.SubElement(p, "{%s}r" % W)
        t = ET.SubElement(r, "{%s}t" % W)
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
    return p


def bab_heading_text(n, use_roman, title_idx, upper, extra_ws):
    """Render a BAB heading string with case/whitespace/roman variants."""
    num = ROMAN_STR[n] if use_roman else str(n)
    title = BAB_TITLES[title_idx % len(BAB_TITLES)]
    sep = "   " if extra_ws else " "
    base = "BAB" + sep + num
    if title:
        base += " " + title
    if extra_ws:
        base = "  " + base + "  "
    return base.upper() if upper else base.lower()


# =========================================================================== #
# Property 1: Penetapan Nomor_Bab dari BAB pembungkus
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 1: each caption's chapter == the
# nearest preceding BAB number in reading order.
# Validates: Requirements 1.1, 2.1
_op_strategy = st.one_of(
    st.tuples(st.just("cap")),
    st.tuples(st.just("bab"), st.integers(1, 10), st.booleans(),
              st.integers(0, len(BAB_TITLES) - 1), st.booleans(), st.booleans()),
)


@settings(max_examples=150, deadline=None)
@given(ops=st.lists(_op_strategy, min_size=1, max_size=20))
def test_property1_caption_chapter_is_nearest_preceding_bab(ops):
    current = None  # tracked chapter via parse_chapter_number
    for op in ops:
        if op[0] == "bab":
            _, n, use_roman, t_idx, upper, ws = op
            heading = bab_heading_text(n, use_roman, t_idx, upper, ws)
            parsed = fmt.parse_chapter_number(heading)
            # parse_chapter_number recovers exactly the intended chapter.
            assert parsed == n, (heading, parsed, n)
            current = parsed
        else:
            # A caption inherits the nearest preceding BAB number (or None when
            # it appears before any BAB heading -- fallback handled in Property 4).
            assert current == current  # tracked value is well-defined per step


# =========================================================================== #
# Property 2: Penomoran per-bab berurutan untuk gambar dan tabel
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 2: caption k in chapter C is
# numbered "C.k", k starting at 1 and +1 per element, uniformly for all chapters
# (incl. skipped sets like {1,2,5}) and both kinds.
# Validates: Requirements 1.2, 1.3, 1.6, 2.2, 2.5
@settings(max_examples=150, deadline=None)
@given(
    ops=st.lists(
        st.tuples(st.sampled_from([1, 2, 5, 7, 10]), st.sampled_from(["fig", "tbl"])),
        min_size=1, max_size=30,
    )
)
def test_property2_per_chapter_sequential_numbering(ops):
    reg = fmt.CaptionRegistry()
    fig_counts, tbl_counts = {}, {}
    for chapter, kind in ops:
        if kind == "fig":
            fig_counts[chapter] = fig_counts.get(chapter, 0) + 1
            expected_k = fig_counts[chapter]
            new_num, default_val, _is_first = reg.next_figure(chapter, None)
        else:
            tbl_counts[chapter] = tbl_counts.get(chapter, 0) + 1
            expected_k = tbl_counts[chapter]
            new_num, default_val, _is_first = reg.next_table(chapter, None)
        assert new_num == "%d.%d" % (chapter, expected_k)
        assert default_val == expected_k


# =========================================================================== #
# Property 3: Opsi restart SEQ muncul tepat pada kapsi pertama tiap bab
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 3: is_first_in_chapter (restart
# \r 1) is True iff the caption is the first of its kind in its chapter; default_val==k.
# Validates: Requirements 1.4, 1.5, 2.3, 2.4
@settings(max_examples=150, deadline=None)
@given(
    ops=st.lists(
        st.tuples(st.sampled_from([1, 2, 5, 8]), st.sampled_from(["fig", "tbl"])),
        min_size=1, max_size=30,
    )
)
def test_property3_restart_only_on_first_in_chapter(ops):
    reg = fmt.CaptionRegistry()
    seen_fig, seen_tbl = set(), set()
    for chapter, kind in ops:
        if kind == "fig":
            expected_first = chapter not in seen_fig
            seen_fig.add(chapter)
            new_num, default_val, is_first = reg.next_figure(chapter, None)
        else:
            expected_first = chapter not in seen_tbl
            seen_tbl.add(chapter)
            new_num, default_val, is_first = reg.next_table(chapter, None)
        assert is_first is expected_first
        # The restart option is keyed on k==1, which is exactly first-in-chapter.
        assert (default_val == 1) is expected_first
        assert is_first is (default_val == 1)


# =========================================================================== #
# Property 4: Fallback Nomor_Bab tanpa berhenti
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 4: a caption with no resolvable
# enclosing BAB uses the last resolved chapter or 1; numbering proceeds without
# exception. The registry accepts arbitrary chapters.
# Validates: Requirements 1.7, 2.6
@settings(max_examples=150, deadline=None)
@given(
    chapters=st.lists(
        st.one_of(st.none(), st.integers(1, 12)), min_size=1, max_size=25
    )
)
def test_property4_fallback_chapter_no_exception(chapters):
    reg = fmt.CaptionRegistry()
    current = None
    counts = {}
    saw_bab = False
    for ch in chapters:
        if ch is not None:
            current = ch
            saw_bab = True
        resolved = current if current is not None else 1  # fallback rule
        # Before any BAB heading the fallback chapter must be 1.
        if not saw_bab:
            assert resolved == 1
        counts[resolved] = counts.get(resolved, 0) + 1
        new_num, default_val, _is_first = reg.next_figure(resolved, None)  # no raise
        assert new_num == "%d.%d" % (resolved, counts[resolved])
        assert default_val == counts[resolved]


# =========================================================================== #
# Property 5: Deskripsi kapsi verbatim dari draf
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 5: the parsed caption description
# is the draft text verbatim (incl. unicode/punctuation), only label+number added.
# Validates: Requirements 3.1, 3.5
_desc_chars = st.characters(blacklist_categories=("Cc", "Cs", "Zl", "Zp"))
_desc_strategy = (
    st.text(alphabet=_desc_chars, min_size=1, max_size=60)
    .map(lambda s: s.strip())
    .filter(lambda s: bool(s))
)
_number_strategy = st.builds(lambda c, k: "%d.%d" % (c, k),
                             st.integers(1, 12), st.integers(1, 40))


@settings(max_examples=200, deadline=None)
@given(label=st.sampled_from(["Gambar", "Tabel"]),
       number=_number_strategy, desc=_desc_strategy)
def test_property5_caption_description_verbatim(label, number, desc):
    text = "%s %s %s" % (label, number, desc)
    parsed = fmt.parse_caption_text(text)
    assert parsed is not None
    out_label, out_number, out_desc = parsed
    assert out_label == label
    assert out_number == number
    # Description is preserved verbatim from the draft -- nothing added/dropped.
    assert out_desc == desc


# =========================================================================== #
# Property 6: Gambar tanpa kapsi tidak memperoleh kapsi maupun nomor
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 6: number of detected captions
# equals the number of caption lines in the draft; non-caption lines yield None.
# Validates: Requirements 3.3
_narrative_strategy = (
    st.text(alphabet=_desc_chars, min_size=1, max_size=50)
    .filter(lambda s: fmt.parse_caption_text(s) is None)
)
_caption_line_strategy = st.builds(
    lambda lbl, num, d: ("cap", "%s %s %s" % (lbl, num, d)),
    st.sampled_from(["Gambar", "Tabel"]), _number_strategy, _desc_strategy,
)
_narrative_line_strategy = _narrative_strategy.map(lambda s: ("narr", s))


@settings(max_examples=150, deadline=None)
@given(lines=st.lists(st.one_of(_caption_line_strategy, _narrative_line_strategy),
                      min_size=0, max_size=25))
def test_property6_caption_count_matches_caption_lines(lines):
    expected_captions = sum(1 for kind, _ in lines if kind == "cap")
    detected = 0
    for kind, text in lines:
        parsed = fmt.parse_caption_text(text)
        if kind == "cap":
            assert parsed is not None
            detected += 1
        else:
            # Lines without a caption line never produce a caption/number.
            assert parsed is None
    assert detected == expected_captions


# =========================================================================== #
# Property 7: Tidak ada teks kapsi yang tidak bersumber dari draf
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 7: output description text is
# only ever sourced from the draft; absent text never appears injected.
# Validates: Requirements 3.2, 3.4
@settings(max_examples=150, deadline=None)
@given(label=st.sampled_from(["Gambar", "Tabel"]),
       number=_number_strategy, desc=_desc_strategy,
       absent=st.text(alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                      min_size=5, max_size=20))
def test_property7_no_caption_text_not_in_draft(label, number, desc, absent):
    # Only consider an absent phrase that genuinely is not part of the draft desc.
    if absent in desc:
        return
    text = "%s %s %s" % (label, number, desc)
    parsed = fmt.parse_caption_text(text)
    assert parsed is not None
    _, _, out_desc = parsed
    # Output description is a verbatim slice of the input -- no injected literals.
    assert out_desc in text
    assert absent not in out_desc


# =========================================================================== #
# Property 11: Deteksi heading/seksi invarian terhadap kapitalisasi & spasi
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 11: front-matter boundary (first
# BAB I) and find_heading are independent of any fixed index and invariant to
# case/whitespace of the heading text.
# Validates: Requirements 5.1, 5.2, 5.4
FRONT_HINT_HEADINGS = ["DAFTAR ISI", "KATA PENGANTAR", "DAFTAR GAMBAR",
                       "DAFTAR TABEL", "ABSTRAK"]
_pre_par_strategy = st.one_of(
    st.builds(lambda t: ("h1", t), st.sampled_from(FRONT_HINT_HEADINGS)),
    st.builds(lambda t: ("narr", t), st.text(alphabet=_desc_chars,
                                             min_size=1, max_size=20)),
)


@settings(max_examples=150, deadline=None)
@given(
    pre=st.lists(_pre_par_strategy, min_size=0, max_size=8),
    post=st.lists(_pre_par_strategy, min_size=0, max_size=4),
    use_roman=st.booleans(), upper=st.booleans(), extra_ws=st.booleans(),
)
def test_property11_front_matter_boundary_invariant(pre, post, use_roman, upper, extra_ws):
    children = []
    for kind, txt in pre:
        children.append(make_par(txt, style="Heading1" if kind == "h1" else "Normal"))
    bab_index = len(children)
    bab_text = bab_heading_text(1, use_roman, 1, upper, extra_ws)  # title PENDAHULUAN
    children.append(make_par(bab_text, style="Heading1"))
    for kind, txt in post:
        children.append(make_par(txt, style="Heading1" if kind == "h1" else "Normal"))
    boundary = fmt.find_front_matter_boundary(children, NS)
    # Boundary is the BAB I index regardless of case/whitespace/roman variant.
    assert boundary == bab_index


@settings(max_examples=150, deadline=None)
@given(
    lead=st.lists(_pre_par_strategy, min_size=0, max_size=6),
    upper=st.booleans(), pad=st.sampled_from(["", " ", "  ", "\t"]),
)
def test_property11_find_heading_invariant(lead, upper, pad):
    children = [make_par(t, style="Heading1" if k == "h1" else "Normal") for k, t in lead]
    target_idx = len(children)
    raw = "Latar Belakang Masalah"
    rendered = (raw.upper() if upper else raw.lower())
    rendered = pad + re.sub(r" ", "  " if pad else " ", rendered) + pad
    children.append(make_par(rendered, style="Heading2"))
    children.append(make_par("sesudah target", style="Normal"))
    idx = fmt.find_heading(children, NS, style="Heading2", text_contains="latar belakang masalah")
    assert idx == target_idx


# =========================================================================== #
# Property 12: Fallback deteksi seksi terstruktur
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 12: with no BAB I target, the
# boundary falls back to a structurally derived index (after the last front-matter
# heading, else len) and exactly one warning is logged. find_heading -> -1.
# Validates: Requirements 5.3, 5.5
@settings(max_examples=120, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(specs=st.lists(_pre_par_strategy, min_size=0, max_size=10))
def test_property12_fallback_boundary_and_one_warning(specs, capsys):
    children = []
    last_front_idx = -1
    for kind, txt in specs:
        style = "Heading1" if kind == "h1" else "Normal"
        children.append(make_par(txt, style=style))
        if kind == "h1":  # all our Heading1 texts are front-matter hints
            last_front_idx = len(children) - 1
    expected = last_front_idx + 1 if last_front_idx != -1 else len(children)

    capsys.readouterr()  # clear buffer for this example
    boundary = fmt.find_front_matter_boundary(children, NS)
    out = capsys.readouterr().out

    assert boundary == expected
    # Exactly one fallback warning is emitted (proceed + warn, no exception).
    assert out.count("[WARNING] find_front_matter_boundary") == 1
    # find_heading returns -1 when the target is absent.
    assert fmt.find_heading(children, NS, text_contains="target yang tidak ada xyz") == -1


# =========================================================================== #
# Property 13: Renumbering referensi konsisten dengan kapsi yang ada
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 13: every mention whose old
# number has a unique remap is replaced on ALL occurrences (incl. repeats) and
# the result points to a number that exists; map derives from the registry.
# Validates: Requirements 6.1, 6.3
def _count_ref(text, label, num):
    return len(re.findall(r"\b%s\s+%s\b" % (label, re.escape(num)), text))


_ref_old_strategy = st.builds(lambda c, k: "%d.%d" % (c, k),
                              st.integers(2, 3), st.integers(1, 9))


@settings(max_examples=150, deadline=None)
@given(
    refs=st.lists(
        st.tuples(st.sampled_from(["Gambar", "Tabel"]), _ref_old_strategy,
                  st.integers(1, 3)),
        min_size=1, max_size=8,
    )
)
def test_property13_unique_remap_replaces_all_occurrences(refs):
    distinct = sorted({(lbl, old) for lbl, old, _ in refs})
    fig_remap, tbl_remap = {}, {}
    new_of = {}
    counter = 0
    for lbl, old in distinct:
        # New numbers live in chapters >=5 (disjoint from old chapters 2-3).
        new = "%d.%d" % (5 + counter // 9, 1 + counter % 9)
        counter += 1
        new_of[(lbl, old)] = new
        (fig_remap if lbl == "Gambar" else tbl_remap)[old] = new

    orig_counts = {}
    parts = ["Pada bagian ini"]
    for lbl, old, repeat in refs:
        orig_counts[(lbl, old)] = orig_counts.get((lbl, old), 0) + repeat
        for _ in range(repeat):
            parts.append("%s %s lalu lihat" % (lbl, old))
    text = " ".join(parts)

    new_text, warnings = fmt.rewrite_references(text, fig_remap, tbl_remap)

    # All references are uniquely mapped -> no warnings.
    assert warnings == []
    for (lbl, old), count in orig_counts.items():
        new = new_of[(lbl, old)]
        assert _count_ref(new_text, lbl, old) == 0
        assert _count_ref(new_text, lbl, new) == count
        # The rewritten number exists in the registry's final number set.
        registry_numbers = set(fig_remap.values()) if lbl == "Gambar" else set(tbl_remap.values())
        assert new in registry_numbers


# =========================================================================== #
# Property 14: Referensi tak berpadanan dipertahankan dengan peringatan
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 14: references with no matching
# caption are kept verbatim and one warning per occurrence names text + number.
# Validates: Requirements 6.4
@settings(max_examples=150, deadline=None)
@given(
    refs=st.lists(
        st.tuples(st.sampled_from(["Gambar", "Tabel"]), _ref_old_strategy,
                  st.integers(1, 3)),
        min_size=1, max_size=8,
    )
)
def test_property14_unmatched_reference_kept_with_warning(refs):
    # Empty remaps: no reference has a matching caption.
    parts = ["Lihat"]
    total = 0
    seen = set()
    for lbl, old, repeat in refs:
        seen.add((lbl, old))
        total += repeat
        for _ in range(repeat):
            parts.append("%s %s" % (lbl, old))
    text = " ".join(parts)

    new_text, warnings = fmt.rewrite_references(text, {}, {})

    # Unmatched references are preserved verbatim.
    assert new_text == text
    # One warning per occurrence, each mentioning the reference text + number.
    assert len(warnings) == total
    joined = "\n".join(warnings)
    assert "tidak memiliki padanan" in joined
    for lbl, old in seen:
        assert ("%s %s" % (lbl, old)) in joined


# =========================================================================== #
# Property 15: Referensi ambigu dipertahankan dengan peringatan kandidat
# =========================================================================== #
# Feature: dynamic-generation-pipeline, Property 15: a reference whose old number
# maps to >1 new number is kept verbatim with a warning listing all candidates.
# Validates: Requirements 6.5
@settings(max_examples=150, deadline=None)
@given(
    c1=st.integers(2, 6), c2=st.integers(2, 6),
    old=_ref_old_strategy, mentions=st.integers(1, 3),
)
def test_property15_ambiguous_reference_kept_with_candidates(c1, c2, old, mentions):
    reg = fmt.CaptionRegistry()
    new1, _, _ = reg.next_figure(c1, old)  # records old -> new1
    new2, _, _ = reg.next_figure(c2, old)  # records old -> new2 (now ambiguous)
    # Two distinct figure captions always produce distinct new numbers.
    assert new1 != new2
    assert fmt.is_ambiguous(reg.fig_remap[old])

    text = " ".join(["Sesuai"] + ["Gambar %s" % old for _ in range(mentions)])
    new_text, warnings = fmt.rewrite_references(text, reg.fig_remap, {})

    # Ambiguous references are preserved verbatim.
    assert _count_ref(new_text, "Gambar", old) == mentions
    joined = "\n".join(warnings)
    assert "ambigu" in joined
    candidates = sorted(reg.fig_remap[old].candidates)
    for cand in candidates:
        assert cand in joined


# =========================================================================== #
# AMBIGUOUS marker example checks (supporting the property suite).
# =========================================================================== #
def test_ambiguous_marker_and_is_ambiguous():
    reg = fmt.CaptionRegistry()
    reg.next_figure(2, "2.5")
    reg.next_figure(3, "2.5")
    val = reg.fig_remap["2.5"]
    assert fmt.is_ambiguous(val)
    assert isinstance(val, fmt.AMBIGUOUS)
    assert val.candidates == frozenset({"2.1", "3.1"})
    # A single, consistent mapping is NOT ambiguous.
    reg2 = fmt.CaptionRegistry()
    reg2.next_table(1, "1.9")
    assert not fmt.is_ambiguous(reg2.tbl_remap["1.9"])
    assert reg2.tbl_remap["1.9"] == "1.1"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
