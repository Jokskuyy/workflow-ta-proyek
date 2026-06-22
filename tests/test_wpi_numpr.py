"""Unit tests for the optional Word numbering (numPr) path of ordered lists
(R4) of the writing-pipeline-improvements spec.

Spec: .kiro/specs/writing-pipeline-improvements

Covers:
  * R4.1 — WHERE Word numbering (numPr) is enabled, build_p_element renders the
    ordered-list item via numbering properties (numId/ilvl) instead of a literal
    textual marker.
  * R4.2 / R4.3 — WHERE numbering is NOT enabled (default), build_p_element keeps
    the literal textual marker, byte-identical to Output_Baseline (Opt_In_By_Content).

build_p_element emits a self-contained ``w:p`` element so these are cheap,
deterministic unit tests (no I/O).
"""
import sys
from pathlib import Path

import lxml.etree

# --------------------------------------------------------------------------- #
# Import from the canonical Mesin_Merge script.
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "scratch"
sys.path.insert(0, str(SCRATCH))

import merge_draft_to_docx as mrg  # noqa: E402

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _q(tag):
    return f"{{{NS}}}{tag}"


def _serialize(el):
    return lxml.etree.tostring(el)


# --------------------------------------------------------------------------- #
# Frozen baseline builder: a VERBATIM snapshot of the pre-numPr list_item
# rendering (literal textual marker run). Used as the preservation oracle for
# R4.2/R4.3 so the default path is proven byte-identical to Output_Baseline.
# DO NOT track refactors here - this is intentionally frozen.
# --------------------------------------------------------------------------- #
def _baseline_list_p(item):
    ns_uri = NS
    p = lxml.etree.Element(f'{{{ns_uri}}}p')
    pPr = lxml.etree.Element(f'{{{ns_uri}}}pPr')
    p.append(pPr)

    lxml.etree.SubElement(pPr, f'{{{ns_uri}}}pStyle', {f'{{{ns_uri}}}val': 'ListParagraph'})

    left_dxa = str(item['level'] * 360)
    lxml.etree.SubElement(pPr, f'{{{ns_uri}}}ind', {
        f'{{{ns_uri}}}left': left_dxa,
        f'{{{ns_uri}}}hanging': '360'
    })

    lxml.etree.SubElement(pPr, f'{{{ns_uri}}}spacing', {
        f'{{{ns_uri}}}before': '0',
        f'{{{ns_uri}}}after': '0',
        f'{{{ns_uri}}}line': '360',
        f'{{{ns_uri}}}lineRule': 'auto'
    })

    lxml.etree.SubElement(pPr, f'{{{ns_uri}}}jc', {f'{{{ns_uri}}}val': 'both'})

    marker_run = lxml.etree.SubElement(p, f'{{{ns_uri}}}r')
    marker_rPr = lxml.etree.SubElement(marker_run, f'{{{ns_uri}}}rPr')
    lxml.etree.SubElement(marker_rPr, f'{{{ns_uri}}}rFonts', {
        f'{{{ns_uri}}}ascii': 'Times New Roman',
        f'{{{ns_uri}}}hAnsi': 'Times New Roman'
    })
    lxml.etree.SubElement(marker_rPr, f'{{{ns_uri}}}sz', {f'{{{ns_uri}}}val': '24'})
    lxml.etree.SubElement(marker_rPr, f'{{{ns_uri}}}szCs', {f'{{{ns_uri}}}val': '24'})

    marker_t = lxml.etree.SubElement(marker_run, f'{{{ns_uri}}}t')
    marker_t.text = item['marker'] + "\t"
    marker_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

    mrg.add_formatted_text(p, item['text'])
    return p


# --------------------------------------------------------------------------- #
# R4.1 — numPr enabled -> numbering properties, no literal marker.
# --------------------------------------------------------------------------- #
def test_r41_numpr_enabled_emits_numpr_element():
    item = {'type': 'list_item', 'level': 1, 'marker': '1.', 'text': 'First item',
            'use_numpr': True}
    p = mrg.build_p_element(item)

    pPr = p.find(_q('pPr'))
    numPr = pPr.find(_q('numPr'))
    assert numPr is not None, "numPr element must be present when numbering is enabled"

    ilvl = numPr.find(_q('ilvl'))
    numId = numPr.find(_q('numId'))
    assert ilvl is not None and numId is not None
    # level 1 -> ilvl 0 (0-based), default numId 1.
    assert ilvl.get(_q('val')) == '0'
    assert numId.get(_q('val')) == '1'


def test_r41_numpr_replaces_literal_marker_run():
    item = {'type': 'list_item', 'level': 1, 'marker': '1.', 'text': 'First item',
            'use_numpr': True}
    p = mrg.build_p_element(item)

    # No literal marker text ("1.\t") should be emitted on the numPr path.
    texts = [t.text for t in p.iter(_q('t'))]
    assert "1.\t" not in texts
    assert all((t is None) or (not t.startswith('1.\t')) for t in texts)

    # The visible content text is still rendered.
    assert "First item" in "".join(t for t in texts if t)


def test_r41_numpr_ilvl_follows_nesting_level():
    item = {'type': 'list_item', 'level': 3, 'marker': 'a.', 'text': 'Deep item',
            'use_numpr': True, 'num_id': 7}
    p = mrg.build_p_element(item)

    numPr = p.find(_q('pPr')).find(_q('numPr'))
    assert numPr.find(_q('ilvl')).get(_q('val')) == '2'   # level 3 -> ilvl 2
    assert numPr.find(_q('numId')).get(_q('val')) == '7'  # custom num_id honored


def test_r41_numpr_child_ordering_after_pstyle():
    """numPr must immediately follow pStyle per the CT_PPr child ordering so
    Word accepts the document."""
    item = {'type': 'list_item', 'level': 2, 'marker': '1.', 'text': 'x',
            'use_numpr': True}
    p = mrg.build_p_element(item)
    pPr_children = [lxml.etree.QName(c).localname for c in p.find(_q('pPr'))]
    assert pPr_children[0] == 'pStyle'
    assert pPr_children[1] == 'numPr'


# --------------------------------------------------------------------------- #
# R4.2 / R4.3 — numbering disabled (default) -> literal marker, identical to
# Output_Baseline byte-per-byte.
# --------------------------------------------------------------------------- #
def test_r42_default_has_no_numpr():
    item = {'type': 'list_item', 'level': 1, 'marker': '1.', 'text': 'First item'}
    p = mrg.build_p_element(item)
    assert p.find(_q('pPr')).find(_q('numPr')) is None


def test_r42_explicit_disabled_has_no_numpr():
    item = {'type': 'list_item', 'level': 2, 'marker': 'a.', 'text': 'Item',
            'use_numpr': False}
    p = mrg.build_p_element(item)
    assert p.find(_q('pPr')).find(_q('numPr')) is None


def test_r43_default_is_byte_identical_to_baseline():
    """Without the opt-in trigger the rendering must be byte-identical to the
    frozen baseline textual-marker rendering (Opt_In_By_Content)."""
    samples = [
        {'type': 'list_item', 'level': 1, 'marker': '1.', 'text': 'First item'},
        {'type': 'list_item', 'level': 2, 'marker': 'a.', 'text': 'Nested *italic* item'},
        {'type': 'list_item', 'level': 3, 'marker': '1)', 'text': 'Deep **bold** item'},
        {'type': 'list_item', 'level': 1, 'marker': '10.', 'text': 'Plain text'},
    ]
    for item in samples:
        produced = _serialize(mrg.build_p_element(item))
        baseline = _serialize(_baseline_list_p(item))
        assert produced == baseline, f"default rendering diverged from baseline for {item!r}"


def test_r43_default_keeps_literal_marker_text():
    item = {'type': 'list_item', 'level': 1, 'marker': '1.', 'text': 'First item'}
    p = mrg.build_p_element(item)
    texts = [t.text for t in p.iter(_q('t'))]
    assert "1.\t" in texts
