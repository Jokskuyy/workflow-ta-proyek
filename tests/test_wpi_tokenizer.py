"""Property + unit tests for the PURE inline tokenizer of the
writing-pipeline-improvements spec.

Spec: .kiro/specs/writing-pipeline-improvements

Covers design Properties 6, 7, 8 against the helpers exposed by
``scratch/merge_draft_to_docx.py``:

  TokenKind, InlineToken, tokenize_inline, emit_runs, RelManager.

The tokenizer is a pure, deterministic transform, so 100+ Hypothesis iterations
are cheap. Property 8 is a byte-for-byte PRESERVATION check against the frozen
oracle ``tests/fixtures/oracle_writing.py`` for text that uses only plain text
plus balanced ``**``/``*`` spans (no new inline constructs).
"""
import sys
from pathlib import Path

import lxml.etree
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# --------------------------------------------------------------------------- #
# Import the tokenizer from the canonical Mesin_Merge script + the frozen oracle.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SCRATCH))
sys.path.insert(0, str(FIXTURES))

import merge_draft_to_docx as mrg  # noqa: E402
import oracle_writing as oracle  # noqa: E402

TEXT = mrg.TokenKind.TEXT
CODE = mrg.TokenKind.CODE
LINK = mrg.TokenKind.LINK
NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

# --------------------------------------------------------------------------- #
# Strategies.
# --------------------------------------------------------------------------- #
# Inner content free of any inline-markup metacharacters.
_INNER_ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,"
_inner = st.text(_INNER_ALPHA, min_size=1, max_size=12)

# Link text (no ']') and url (no ')'), kept to a safe alphabet.
_LINK_TEXT_ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ./:-"
_link_text = st.text(_LINK_TEXT_ALPHA, min_size=1, max_size=12)
_URL_ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789./:-_"
_url = st.text(_URL_ALPHA, min_size=1, max_size=15).map(lambda s: "https://" + s)

# Plain words used by Property 7/8 (never contain a markup metachar).
_PLAIN_ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789 "
_plain0 = st.text(_PLAIN_ALPHA, min_size=0, max_size=8)   # may be empty
_plain1 = st.text(_PLAIN_ALPHA, min_size=1, max_size=8)   # never empty


@st.composite
def balanced_text(draw):
    """Generate text with only plain runs and balanced ``**``/``*`` spans.

    Formatted spans are always separated by a NON-EMPTY plain chunk, so adjacent
    markers can never collapse into ``***`` or an empty ``****`` span. No new
    inline constructs (code/link/escape) are ever produced.
    """
    n = draw(st.integers(min_value=0, max_value=4))
    parts = [draw(_plain0)]  # leading plain text (may be empty)
    for _ in range(n):
        word = draw(_plain1)
        if draw(st.booleans()):
            parts.append("**" + word + "**")
        else:
            parts.append("*" + word + "*")
        parts.append(draw(_plain1))  # mandatory non-empty separator
    return "".join(parts)


def _make_default_rPr(enabled):
    """Optionally build a default rPr (bold) like a table-header cell uses."""
    if not enabled:
        return None
    d = lxml.etree.Element(f'{{{NS}}}rPr')
    lxml.etree.SubElement(d, f'{{{NS}}}b')
    lxml.etree.SubElement(d, f'{{{NS}}}bCs')
    return d


# =========================================================================== #
# Property 6: Kebenaran format token inline
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 6: Kebenaran format token inline
# Validates: Requirements 2.1, 2.2, 2.3, 2.5, 2.6
@settings(max_examples=200, deadline=None)
@given(inner=_inner, kind=st.sampled_from(["bold", "italic", "both", "code"]))
def test_property6_token_format_correctness(inner, kind):
    if kind == "bold":
        assert mrg.tokenize_inline(f"**{inner}**") == [
            mrg.InlineToken(TEXT, inner, bold=True)
        ]
    elif kind == "italic":
        assert mrg.tokenize_inline(f"*{inner}*") == [
            mrg.InlineToken(TEXT, inner, italic=True)
        ]
    elif kind == "both":
        assert mrg.tokenize_inline(f"***{inner}***") == [
            mrg.InlineToken(TEXT, inner, bold=True, italic=True)
        ]
    else:  # code
        assert mrg.tokenize_inline(f"`{inner}`") == [mrg.InlineToken(CODE, inner)]


# Feature: writing-pipeline-improvements, Property 6: Kebenaran format token inline (link)
# Validates: Requirements 2.5, 2.6
@settings(max_examples=200, deadline=None)
@given(t=_link_text, u=_url)
def test_property6_link_token(t, u):
    assert mrg.tokenize_inline(f"[{t}]({u})") == [mrg.InlineToken(LINK, t, url=u)]


# =========================================================================== #
# Property 7: Escape literal dan tanpa kebocoran state
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 7: Escape literal dan tanpa kebocoran state
# Validates: Requirements 2.4, 2.7
@settings(max_examples=200, deadline=None)
@given(pre=_plain0, post=_plain0)
def test_property7_escaped_asterisk_is_literal(pre, post):
    toks = mrg.tokenize_inline(pre + r"\*" + post)
    # No token carries bold/italic state introduced by the escape.
    assert all(t.kind == TEXT and not t.bold and not t.italic for t in toks)
    joined = "".join(t.text for t in toks)
    # Exactly one literal asterisk (pre/post never contain one).
    assert joined == pre + "*" + post
    assert joined.count("*") == 1


# Feature: writing-pipeline-improvements, Property 7: Escape literal dan tanpa kebocoran state
# Validates: Requirements 2.4, 2.7
@settings(max_examples=200, deadline=None)
@given(pre=_plain0, post=_plain0, marker=st.sampled_from(["*", "**"]))
def test_property7_unbalanced_marker_literal_no_leak(pre, post, marker):
    text = pre + marker + post
    toks = mrg.tokenize_inline(text)
    # The orphan marker is literalized: no token inherits bold/italic.
    assert all(not t.bold and not t.italic for t in toks)
    # Reconstructed literal text round-trips exactly (orphan marker kept literal).
    joined = "".join(t.text for t in toks if t.kind == TEXT)
    assert joined == text


# =========================================================================== #
# Property 8: Preservasi tokenizer terhadap baseline (byte-for-byte oracle)
# =========================================================================== #
# Feature: writing-pipeline-improvements, Property 8: Preservasi tokenizer terhadap baseline
# Validates: Requirements 2.8, 2.9
@settings(max_examples=200, deadline=None)
@given(text=balanced_text(), use_default=st.booleans())
def test_property8_preservation_against_oracle(text, use_default):
    p_new = lxml.etree.Element(f'{{{NS}}}p')
    mrg.emit_runs(p_new, mrg.tokenize_inline(text), _make_default_rPr(use_default))

    p_old = lxml.etree.Element(f'{{{NS}}}p')
    oracle.oracle_add_formatted_text(p_old, text, _make_default_rPr(use_default))

    assert oracle.serialize(p_new) == oracle.serialize(p_old)


# =========================================================================== #
# Focused unit examples (cheap sanity checks around the property generators).
# =========================================================================== #
def test_unit_unclosed_code_is_literal_backtick():
    assert mrg.tokenize_inline("a`b") == [mrg.InlineToken(TEXT, "a`b")]


def test_unit_broken_link_is_literal_bracket():
    # No closing ')' -> the '[' is literal, not a LINK.
    assert mrg.tokenize_inline("[text](no-close") == [
        mrg.InlineToken(TEXT, "[text](no-close")
    ]


def test_unit_mixed_constructs_order_preserved():
    toks = mrg.tokenize_inline("see `x` and [g](https://e.com) end")
    assert [t.kind for t in toks] == [TEXT, CODE, TEXT, LINK, TEXT]
    assert toks[1] == mrg.InlineToken(CODE, "x")
    assert toks[3] == mrg.InlineToken(LINK, "g", url="https://e.com")


def test_unit_rel_manager_dedups_identical_urls():
    rm = mrg.RelManager(existing_ids={"rId5"})
    a = rm.add_external("https://example.com")
    b = rm.add_external("https://example.com")
    c = rm.add_external("https://other.com")
    assert a == b            # identical urls share one rId
    assert a != c
    assert "rId5" not in (a, c)  # never collides with existing ids


def test_unit_emit_runs_link_creates_hyperlink_with_rid():
    rm = mrg.RelManager()
    p = lxml.etree.Element(f'{{{NS}}}p')
    mrg.emit_runs(p, mrg.tokenize_inline("[g](https://e.com)"), None, rm)
    hyperlinks = p.findall(f'{{{NS}}}hyperlink')
    assert len(hyperlinks) == 1
    r_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    assert hyperlinks[0].get(f'{{{r_ns}}}id') == rm.add_external("https://e.com")
    assert rm.has_new


def test_unit_emit_runs_without_rel_manager_no_links_unchanged():
    # Plain text without links must not allocate any relationships.
    rm = mrg.RelManager()
    p = lxml.etree.Element(f'{{{NS}}}p')
    mrg.emit_runs(p, mrg.tokenize_inline("just plain **bold** text"), None, rm)
    assert not rm.has_new


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
