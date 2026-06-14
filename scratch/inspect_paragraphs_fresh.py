import xml.etree.ElementTree as ET

def main():
    doc_path = "unpacked_fresh/word/document.xml"
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    ps = root.findall('.//w:p', namespaces)
    print(f"Total paragraphs: {len(ps)}")
    
    for i in range(90, 110):
        if i >= len(ps):
            break
        p = ps[i]
        text = "".join([t.text for t in p.findall('.//w:r/w:t', namespaces)]).strip()
        pStyle = p.find('.//w:pStyle', namespaces)
        style_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else 'Normal'
        
        ind = p.find('.//w:ind', namespaces)
        ind_str = ""
        if ind is not None:
            ind_str = " | left={}, hanging={}, firstLine={}".format(
                ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}left', 'None'),
                ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hanging', 'None'),
                ind.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine', 'None')
            )
        else:
            ind_str = " | No ind"
            
        print(f"P #{i:03d} [Style={style_val:15s}]: '{text[:60]}' {ind_str}")

if __name__ == '__main__':
    main()
