import xml.etree.ElementTree as ET
import os

def extract_text_from_xml(xml_path, output_path):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist.")
        return
        
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # We walk through all paragraphs in the document
        for p in root.findall('.//w:p', namespaces):
            # Check paragraph style (heading, title, etc.)
            pStyle_val = None
            pPr = p.find('w:pPr', namespaces)
            if pPr is not None:
                pStyle = pPr.find('w:pStyle', namespaces)
                if pStyle is not None:
                    pStyle_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            
            # Extract text from all runs in this paragraph
            p_text_parts = []
            for r in p.findall('.//w:r', namespaces):
                t_elems = r.findall('.//w:t', namespaces)
                for t in t_elems:
                    if t.text:
                        p_text_parts.append(t.text)
            
            p_text = "".join(p_text_parts).strip()
            
            if p_text:
                if pStyle_val:
                    f.write(f"[{pStyle_val}] {p_text}\n")
                else:
                    f.write(f"{p_text}\n")
            elif pStyle_val:
                # Empty paragraph but has style (could be spacing or empty heading)
                f.write(f"[{pStyle_val}] (empty)\n")
            else:
                f.write("\n")

if __name__ == '__main__':
    xml_path = r'unpacked_ta/word/document.xml'
    output_path = r'scratch/document_text.txt'
    os.makedirs('scratch', exist_ok=True)
    extract_text_from_xml(xml_path, output_path)
    print("Done! Extracted text saved to scratch/document_text.txt")
