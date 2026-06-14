import xml.etree.ElementTree as ET

def main():
    doc_path = "unpacked_ta_proyek/word/document.xml"
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    body = root.find('w:body', namespaces)
    if body is None:
        print("Body not found")
        return
        
    children = list(body)
    print(f"Total child elements in body: {len(children)}")
    
    # We want to scan for tbl and p (with drawing or caption)
    for idx, child in enumerate(children):
        tag = child.tag.split('}')[-1]
        
        if tag == 'tbl':
            print(f"Index {idx:03d} [TABLE]")
            # Look at paragraph before
            if idx > 0 and children[idx-1].tag.endswith('p'):
                txt = "".join([t.text for t in children[idx-1].findall('.//w:t', namespaces) if t.text]).strip()
                print(f"  Prev P: '{txt}'")
            # Look at paragraph after
            if idx + 1 < len(children) and children[idx+1].tag.endswith('p'):
                txt = "".join([t.text for t in children[idx+1].findall('.//w:t', namespaces) if t.text]).strip()
                print(f"  Next P: '{txt}'")
                
        elif tag == 'p':
            # Check if it contains drawing
            drawing = child.find('.//w:drawing', namespaces)
            if drawing is not None:
                txt = "".join([t.text for t in child.findall('.//w:t', namespaces) if t.text]).strip()
                print(f"Index {idx:03d} [FIGURE PARAGRAPH] text='{txt}'")
                # Look at paragraph before
                if idx > 0 and children[idx-1].tag.endswith('p'):
                    txt_prev = "".join([t.text for t in children[idx-1].findall('.//w:t', namespaces) if t.text]).strip()
                    print(f"  Prev P: '{txt_prev}'")
                # Look at paragraph after
                if idx + 1 < len(children) and children[idx+1].tag.endswith('p'):
                    txt_next = "".join([t.text for t in children[idx+1].findall('.//w:t', namespaces) if t.text]).strip()
                    print(f"  Next P: '{txt_next}'")

if __name__ == '__main__':
    main()
