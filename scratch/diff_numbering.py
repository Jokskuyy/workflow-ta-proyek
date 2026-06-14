import lxml.etree
import sys

def diff_elements(orig_path, new_path):
    orig_tree = lxml.etree.parse(orig_path)
    new_tree = lxml.etree.parse(new_path)
    
    orig_root = orig_tree.getroot()
    new_root = new_tree.getroot()
    
    print("Original element count:", len(orig_root))
    print("New element count:", len(new_root))
    
    orig_tags = [e.tag for e in orig_root]
    new_tags = [e.tag for e in new_root]
    
    # Let's find elements in new that are not in orig
    # or elements that differ
    # We can match them by abstractNumId or numId
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    
    # 1. Compare abstractNum elements
    orig_an = {e.get(f'{{{w}}}abstractNumId'): e for e in orig_root.findall(f'{{{w}}}abstractNum')}
    new_an = {e.get(f'{{{w}}}abstractNumId'): e for e in new_root.findall(f'{{{w}}}abstractNum')}
    
    print("\nAbstractNum comparison:")
    print("  Original abstractNum IDs:", sorted(list(orig_an.keys()), key=int))
    print("  New abstractNum IDs:", sorted(list(new_an.keys()), key=int))
    
    added_an = set(new_an.keys()) - set(orig_an.keys())
    print("  Added abstractNum IDs:", added_an)
    
    # 2. Compare num elements
    orig_num = {e.get(f'{{{w}}}numId'): e for e in orig_root.findall(f'{{{w}}}num')}
    new_num = {e.get(f'{{{w}}}numId'): e for e in new_root.findall(f'{{{w}}}num')}
    
    print("\nNum comparison:")
    print("  Original num IDs:", sorted(list(orig_num.keys()), key=int))
    print("  New num IDs:", sorted(list(new_num.keys()), key=int))
    
    added_num = set(new_num.keys()) - set(orig_num.keys())
    print("  Added num IDs:", added_num)
    
    # Check if any original element was modified
    modified_an = []
    for aid, elem in orig_an.items():
        new_elem = new_an.get(aid)
        if new_elem is None:
            print(f"  Warning: abstractNumId {aid} was deleted!")
            continue
        orig_xml = lxml.etree.tostring(elem)
        new_xml = lxml.etree.tostring(new_elem)
        if orig_xml != new_xml:
            modified_an.append(aid)
            
    print("  Modified abstractNum IDs (should be empty):", modified_an)
    
    modified_num = []
    for nid, elem in orig_num.items():
        new_elem = new_num.get(nid)
        if new_elem is None:
            print(f"  Warning: numId {nid} was deleted!")
            continue
        orig_xml = lxml.etree.tostring(elem)
        new_xml = lxml.etree.tostring(new_elem)
        if orig_xml != new_xml:
            modified_num.append(nid)
            
    print("  Modified num IDs (should be empty):", modified_num)

if __name__ == '__main__':
    diff_elements('unpacked_test_orig/word/numbering.xml', 'unpacked_test_num/word/numbering.xml')
