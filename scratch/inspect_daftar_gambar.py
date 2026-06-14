import xml.etree.ElementTree as ET

def main():
    doc_path = "unpacked_fresh/word/document.xml"
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    body = root.find('w:body', namespaces)
    children = list(body)
    
    # Find DAFTAR GAMBAR index
    idx = -1
    for i, child in enumerate(children):
        if child.tag.endswith('p'):
            txt = "".join([t.text for t in child.findall('.//w:t', namespaces) if t.text]).strip()
            if txt == 'DAFTAR GAMBAR':
                idx = i
                break
                
    if idx == -1:
        print("DAFTAR GAMBAR not found")
        return
        
    print(f"DAFTAR GAMBAR found at index {idx}")
    
    # Print the next 10 elements in body
    for i in range(idx, idx + 15):
        if i >= len(children):
            break
        child = children[i]
        tag = child.tag.split('}')[-1]
        
        if tag == 'p':
            txt = "".join([t.text for t in child.findall('.//w:t', namespaces) if t.text]).strip()
            # Let's check for instrText in fields (TOC etc.)
            instrs = [t.text for t in child.findall('.//w:instrText', namespaces) if t.text]
            instr_str = " | instrs=" + str(instrs) if instrs else ""
            print(f"Index {i:03d} [P] (style={child.find('.//w:pStyle', namespaces).get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if child.find('.//w:pStyle', namespaces) is not None else 'Normal'}): '{txt[:100]}' {instr_str}")
        elif tag == 'sdt':
            print(f"Index {i:03d} [SDT]")
            # Check runs inside SDT
            sdtContent = child.find('.//w:sdtContent', namespaces)
            if sdtContent is not None:
                for j, sdt_child in enumerate(list(sdtContent)[:5]):
                    sdt_txt = "".join([t.text for t in sdt_child.findall('.//w:t', namespaces) if t.text]).strip()
                    print(f"  SDT Child {j}: '{sdt_txt[:80]}'")
        else:
            print(f"Index {i:03d} [{tag}]")

if __name__ == '__main__':
    main()
