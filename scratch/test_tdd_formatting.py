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
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
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

if __name__ == '__main__':
    unittest.main()
