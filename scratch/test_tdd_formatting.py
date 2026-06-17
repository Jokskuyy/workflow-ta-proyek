import unittest
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
import sys

# Append the scripts directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../skills/docx-ta-proyek/scripts")))
import format_ta_proyek

class TestTddFormatting(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.word_dir = os.path.join(self.test_dir, "word")
        os.makedirs(self.word_dir)
        
        # Write dummy styles.xml
        self.styles_path = os.path.join(self.word_dir, "styles.xml")
        with open(self.styles_path, "w", encoding="utf-8") as f:
            f.write('<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"></w:styles>')
            
        self.doc_path = os.path.join(self.word_dir, "document.xml")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def write_document_xml(self, paragraphs_xml_str):
        xml_content = f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r>
        <w:t>BAB I PENDAHULUAN</w:t>
      </w:r>
    </w:p>
    {paragraphs_xml_str}
  </w:body>
</w:document>
"""
        with open(self.doc_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

    def find_paragraph_by_text(self, root, namespaces, search_text):
        for p in root.findall('.//w:p', namespaces):
            text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text])
            if search_text in text:
                return p
        return None

    def test_reconstruct_figure_caption_clean(self):
        # We test that caption for first figure is reconstructed with "SEQ Gambar \r 1 \* ARABIC"
        p_xml = """
        <w:p>
          <w:pPr><w:pStyle w:val="Caption"/></w:pPr>
          <w:r><w:t>Gambar 2.1 Hasil Kuesioner: Profil Status Akademik Responden</w:t></w:r>
        </w:p>
        """
        self.write_document_xml(p_xml)
        
        # Run formatting script
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        # Read formatted XML
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        p_caption = self.find_paragraph_by_text(root, namespaces, "Hasil Kuesioner")
        self.assertIsNotNone(p_caption, "Caption paragraph not found in output document")
        
        # Verify paragraph style is Caption
        pStyle = p_caption.find('.//w:pStyle', namespaces)
        self.assertIsNotNone(pStyle)
        self.assertEqual(pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'Caption')
        
        # Verify there is a SEQ field with name 'Gambar' and restart switch '\r 1'
        instr = p_caption.find('.//w:instrText', namespaces)
        self.assertIsNotNone(instr)
        self.assertEqual(instr.text.strip(), 'SEQ Gambar \\r 1 \\* ARABIC')
        
        # Verify text elements
        t_elems = p_caption.findall('.//w:t', namespaces)
        self.assertTrue(len(t_elems) >= 3)
        self.assertEqual(t_elems[0].text, 'Gambar 2.')
        self.assertEqual(t_elems[-1].text, ' Hasil Kuesioner: Profil Status Akademik Responden')

    def test_appendix_heading_formatting_no_numpr(self):
        p_xml = """
        <w:p>
          <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
          <w:r><w:t>LAMPIRAN 1. Surat Pernyataan Keaslian</w:t></w:r>
        </w:p>
        """
        self.write_document_xml(p_xml)
        
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        p_appendix = self.find_paragraph_by_text(root, namespaces, "Surat Pernyataan Keaslian")
        self.assertIsNotNone(p_appendix, "Appendix paragraph not found in output document")
        
        pPr = p_appendix.find('w:pPr', namespaces)
        self.assertIsNotNone(pPr)
        
        # Verify style is taappendixheading
        pStyle = pPr.find('w:pStyle', namespaces)
        self.assertIsNotNone(pStyle)
        self.assertEqual(pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'taappendixheading')
        
        # Verify numPr is completely absent
        numPr = pPr.find('w:numPr', namespaces)
        self.assertIsNone(numPr, "Appendix heading should NOT have w:numPr auto-numbering")
        
        # Verify style in styles.xml has outlineLvl 8
        styles_tree = ET.parse(self.styles_path)
        styles_root = styles_tree.getroot()
        app_style = styles_root.find("w:style[@w:styleId='taappendixheading']", namespaces)
        self.assertIsNotNone(app_style)
        
        style_pPr = app_style.find('w:pPr', namespaces)
        self.assertIsNotNone(style_pPr)
        outlineLvl = style_pPr.find('w:outlineLvl', namespaces)
        self.assertIsNotNone(outlineLvl, "Appendix style should have w:outlineLvl to map to Level 9")
        self.assertEqual(outlineLvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), '8')
        
        # Verify TOC9 style has zero indentation
        toc9_style = styles_root.find("w:style[@w:styleId='TOC9']", namespaces)
        self.assertIsNotNone(toc9_style)
        toc9_pPr = toc9_style.find('w:pPr', namespaces)
        self.assertIsNotNone(toc9_pPr)
        toc9_ind = toc9_pPr.find('w:ind', namespaces)
        self.assertEqual(toc9_ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left'), '1')
            
        # Verify Table of Appendices field instruction maps outline levels 9-9
        p_lampiran_toc = self.find_paragraph_by_text(root, namespaces, "DAFTAR LAMPIRAN")
        body = root.find('w:body', namespaces)
        p_elements = body.findall('w:p', namespaces)
        idx_lampiran = p_elements.index(p_lampiran_toc)
        p_toc = p_elements[idx_lampiran + 1]
        instr_toc = p_toc.find('.//w:instrText', namespaces)
        self.assertIsNotNone(instr_toc)
        self.assertTrue('TOC \\o "9-9" \\n 9-9' in instr_toc.text)

    def test_reconstruct_table_caption_clean(self):
        p_xml = """
        <w:p>
          <w:pPr><w:pStyle w:val="Caption"/></w:pPr>
          <w:r><w:t>Tabel 1.1 Peran dan Tanggung Jawab</w:t></w:r>
        </w:p>
        """
        self.write_document_xml(p_xml)
        
        # Run formatting script
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        # Read formatted XML
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        p_caption = self.find_paragraph_by_text(root, namespaces, "Peran dan Tanggung Jawab")
        self.assertIsNotNone(p_caption, "Table caption paragraph not found in output document")
        
        # Verify paragraph style is Caption
        pStyle = p_caption.find('.//w:pStyle', namespaces)
        self.assertIsNotNone(pStyle)
        self.assertEqual(pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'Caption')
        
        # Verify there is a SEQ field with name 'Tabel' and restart switch '\r 1' since it is the first table
        instr = p_caption.find('.//w:instrText', namespaces)
        self.assertIsNotNone(instr)
        self.assertEqual(instr.text.strip(), 'SEQ Tabel \\r 1 \\* ARABIC')
        
        # Verify text elements
        t_elems = p_caption.findall('.//w:t', namespaces)
        self.assertTrue(len(t_elems) >= 3)
        self.assertEqual(t_elems[0].text, 'Tabel 1.')
        self.assertEqual(t_elems[-1].text, ' Peran dan Tanggung Jawab')

    def test_drawing_paragraph_has_keepnext(self):
        p_xml = """
        <w:p>
          <w:pPr><w:pStyle w:val="Normal"/></w:pPr>
          <w:r>
            <w:drawing>
              <wp:inline>
                <wp:extent cx="1000" cy="1000"/>
              </wp:inline>
            </w:drawing>
          </w:r>
        </w:p>
        """
        self.write_document_xml(p_xml)
        
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
        }
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        p_draw = root.find('.//w:drawing/../..', namespaces)
        self.assertIsNotNone(p_draw, "Paragraph containing drawing not found")
        
        pPr = p_draw.find('w:pPr', namespaces)
        self.assertIsNotNone(pPr, "w:pPr not found in drawing paragraph")
        
        keep_next = pPr.find('w:keepNext', namespaces)
        self.assertIsNotNone(keep_next, "w:keepNext element should be present in drawing paragraph properties")

    def test_drawing_crop_deletion(self):
        p_xml = """
        <w:p>
          <w:pPr><w:pStyle w:val="Normal"/></w:pPr>
          <w:r>
            <w:drawing>
              <wp:inline>
                <wp:extent cx="1000" cy="1000"/>
                <a:graphic>
                  <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                    <pic:pic>
                      <pic:blipFill>
                        <a:blip r:embed="rId9"/>
                        <a:srcRect l="10" t="20" r="30" b="40"/>
                      </pic:blipFill>
                    </pic:pic>
                  </a:graphicData>
                </a:graphic>
              </wp:inline>
            </w:drawing>
          </w:r>
        </w:p>
        """
        self.write_document_xml(p_xml)
        
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'
        }
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        src_rects = root.findall('.//a:srcRect', namespaces)
        self.assertEqual(len(src_rects), 0, "All a:srcRect elements must be completely deleted")

    def test_lembar_pengesahan_isolation(self):
        xml_content = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    <w:p>
      <w:r>
        <w:drawing>
          <wp:inline><wp:extent cx="1000" cy="1000"/></wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    <w:p>
      <w:r><w:t>PROPOSAL TUGAS AKHIR</w:t></w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:drawing>
          <wp:inline><wp:extent cx="1000" cy="1000"/></wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    <w:p/>
    <w:p>
      <w:r><w:t>DAFTAR ISI</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r>
        <w:t>BAB I PENDAHULUAN</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
"""
        with open(self.doc_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
            
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        body = root.find('w:body', namespaces)
        paragraphs = body.findall('w:p', namespaces)
        
        draw_paras = []
        for p in paragraphs:
            if p.find('.//w:drawing', namespaces) is not None:
                draw_paras.append(p)
                
        self.assertEqual(len(draw_paras), 2, "Should have cover logo and lembar pengesahan drawings")
        lp_para = draw_paras[1]
        
        pPr_lp = lp_para.find('w:pPr', namespaces)
        self.assertIsNotNone(pPr_lp, "Lembar Pengesahan should have w:pPr")
        self.assertIsNotNone(pPr_lp.find('w:pageBreakBefore', namespaces), "Lembar Pengesahan must have pageBreakBefore")
        
        di_para = None
        for p in paragraphs:
            text = "".join(p.itertext()).strip()
            if "DAFTAR ISI" in text:
                di_para = p
                break
                
        self.assertIsNotNone(di_para, "DAFTAR ISI paragraph should be present")
        pPr_di = di_para.find('w:pPr', namespaces)
        self.assertIsNotNone(pPr_di, "DAFTAR ISI should have w:pPr")
        self.assertIsNotNone(pPr_di.find('w:pageBreakBefore', namespaces), "DAFTAR ISI must have pageBreakBefore to isolate Lembar Pengesahan")

    def test_lembar_pengesahan_within_margins(self):
        xml_content = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    <w:p>
      <w:r>
        <w:drawing>
          <wp:inline><wp:extent cx="1000" cy="1000"/></wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    <w:p>
      <w:r><w:t>PROPOSAL TUGAS AKHIR</w:t></w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:drawing>
          <wp:inline>
            <wp:extent cx="5943600" cy="7912100"/>
            <a:graphic>
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic>
                  <pic:blipFill>
                    <a:blip r:embed="rId9"/>
                    <a:srcRect l="10" t="20" r="30" b="40"/>
                  </pic:blipFill>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    <w:p/>
    <w:p>
      <w:r><w:t>DAFTAR ISI</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r>
        <w:t>BAB I PENDAHULUAN</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
"""
        with open(self.doc_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
            
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
        }
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        body = root.find('w:body', namespaces)
        paragraphs = body.findall('w:p', namespaces)
        
        draw_paras = []
        for p in paragraphs:
            if p.find('.//w:drawing', namespaces) is not None:
                draw_paras.append(p)
                
        # Lembar Pengesahan is the second drawing
        lp_para = draw_paras[1]
        
        pPr = lp_para.find('w:pPr', namespaces)
        self.assertIsNotNone(pPr)
        
        # Verify indents are cleared: left='0', firstLine='0', right='0'
        ind = pPr.find('w:ind', namespaces)
        self.assertIsNotNone(ind)
        self.assertEqual(ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left'), '0')
        self.assertEqual(ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine'), '0')
        self.assertEqual(ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}right'), '0')
        
        # Verify drawing size is scaled to width 14.0cm (5040000 EMUs)
        drawing = lp_para.find('.//w:drawing', namespaces)
        extent = drawing.find('.//wp:extent', namespaces)
        self.assertEqual(extent.get('cx'), '5040000')
        self.assertEqual(extent.get('cy'), '6709230') # Scaled proportionally from aspect ratio

    def test_table_centering_and_cell_alignments(self):
        table_xml = """
        <w:tbl>
          <w:tblPr>
            <w:jc w:val="left"/>
          </w:tblPr>
          <w:tr>
            <w:tc>
              <w:tcPr/>
              <w:p>
                <w:pPr><w:jc w:val="left"/></w:pPr>
                <w:r><w:t>Header Cell</w:t></w:r>
              </w:p>
            </w:tc>
          </w:tr>
          <w:tr>
            <w:tc>
              <w:tcPr/>
              <w:p>
                <w:pPr><w:jc w:val="center"/></w:pPr>
                <w:r><w:t>Body Cell</w:t></w:r>
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
        """
        self.write_document_xml(table_xml)
        
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        tbl = root.find('.//w:tbl', namespaces)
        self.assertIsNotNone(tbl)
        
        tblPr = tbl.find('w:tblPr', namespaces)
        self.assertIsNotNone(tblPr)
        
        # Table horizontal alignment must be center
        jc = tblPr.find('w:jc', namespaces)
        self.assertIsNotNone(jc)
        self.assertEqual(jc.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'center')
        
        rows = tbl.findall('w:tr', namespaces)
        self.assertEqual(len(rows), 2)
        
        # Header Row (Row 0)
        h_cell = rows[0].find('w:tc', namespaces)
        h_tcPr = h_cell.find('w:tcPr', namespaces)
        self.assertIsNotNone(h_tcPr)
        v_align_h = h_tcPr.find('w:vAlign', namespaces)
        self.assertIsNotNone(v_align_h)
        self.assertEqual(v_align_h.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'center')
        
        h_p = h_cell.find('w:p', namespaces)
        h_pPr = h_p.find('w:pPr', namespaces)
        self.assertIsNotNone(h_pPr)
        jc_h = h_pPr.find('w:jc', namespaces)
        self.assertIsNotNone(jc_h)
        self.assertEqual(jc_h.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'center')
        
        # Body Row (Row 1)
        b_cell = rows[1].find('w:tc', namespaces)
        b_tcPr = b_cell.find('w:tcPr', namespaces)
        self.assertIsNotNone(b_tcPr)
        v_align_b = b_tcPr.find('w:vAlign', namespaces)
        self.assertIsNotNone(v_align_b)
        self.assertEqual(v_align_b.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'top')
        
        b_p = b_cell.find('w:p', namespaces)
        b_pPr = b_p.find('w:pPr', namespaces)
        self.assertIsNotNone(b_pPr)
        jc_b = b_pPr.find('w:jc', namespaces)
        self.assertIsNotNone(jc_b)
        self.assertEqual(jc_b.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'), 'left')

    def test_front_matter_section_break(self):
        # Setup XML with a paragraph before BAB I PENDAHULUAN
        xml_content = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    <w:p>
      <w:r><w:t>COVER PAGE</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>LEMBAR PENGESAHAN</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>DAFTAR ISI</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r><w:t>BAB I PENDAHULUAN</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Body content</w:t></w:r>
    </w:p>
    <w:sectPr/>
  </w:body>
</w:document>
"""
        with open(self.doc_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
            
        format_ta_proyek.format_document_xmls(self.test_dir)
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tree = ET.parse(self.doc_path)
        root = tree.getroot()
        
        body = root.find('w:body', namespaces)
        paragraphs = body.findall('w:p', namespaces)
        
        # The paragraph preceding BAB I PENDAHULUAN should be the newly inserted empty section break paragraph
        p_sect = paragraphs[5]
        text_sect = "".join(p_sect.itertext()).strip()
        self.assertEqual(text_sect, "")
        
        pPr = p_sect.find('w:pPr', namespaces)
        self.assertIsNotNone(pPr, "Section break paragraph should have a w:pPr element")
        
        sectPr = pPr.find('w:sectPr', namespaces)
        self.assertIsNotNone(sectPr, "Section break (w:sectPr) should be present on dedicated paragraph")
        
        pgNumType = sectPr.find('w:pgNumType', namespaces)
        self.assertIsNotNone(pgNumType, "pgNumType should be present in section break")
        self.assertEqual(pgNumType.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fmt'), 'lowerRoman')
        self.assertEqual(pgNumType.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}start'), '1')

if __name__ == '__main__':
    unittest.main()

