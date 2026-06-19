import os
import sys

try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W15_NS = 'http://schemas.microsoft.com/office/word/2012/wordml'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
NUM_REL_TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering'

LVL_ORDER = [
    'start', 'numFmt', 'lvlRestart', 'pStyle', 'isLgl', 'suff', 
    'lvlText', 'lvlPicBulletId', 'legacy', 'legacySpace', 'legacyIndent', 
    'lvlJc', 'pPr', 'rPr'
]

PRESETS = {
    'thesis': {
        'description': 'Thesis/Skripsi: 1. -> a. -> 1) -> a)',
        'levels': [
            ('decimal', '%1.', 'left', 720, 360),
            ('lowerLetter', '%2.', 'left', 1440, 360),
            ('decimal', '%3)', 'left', 2160, 360),
            ('lowerLetter', '%4)', 'left', 2880, 360),
            ('decimal', '(%5)', 'left', 3600, 360),
            ('lowerLetter', '(%6)', 'left', 4320, 360),
            ('lowerRoman', '%7.', 'right', 5040, 360),
            ('decimal', '%8.', 'left', 5760, 360),
            ('lowerLetter', '%9.', 'left', 6480, 360),
        ]
    },
    'thesis-heading': {
        'description': 'Thesis Headings: BAB 1. -> 1.1. -> 2.1.1. -> 3.1.1.1. (UPN Thesis)',
        'levels': [
            ('decimal', 'BAB %1.', 'left', 0, 0),
            ('decimal', '%1.%2.', 'left', 0, 0),
            ('decimal', '%1.%2.%3.', 'left', 0, 0),
            ('decimal', '%1.%2.%3.%4.', 'left', 0, 0),
            ('lowerLetter', '%5.', 'left', 0, 0),
            ('decimal', '%6)', 'left', 0, 0),
            ('lowerLetter', '%7)', 'left', 0, 0),
            ('lowerRoman', '%8.', 'right', 0, 0),
            ('decimal', '%9.', 'left', 0, 0),
        ]
    }
}

def sort_element_children(parent, order_list):
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    def key_func(child):
        tag = child.tag
        local_name = tag[len(f'{{{ns_uri}}}'):] if tag.startswith(f'{{{ns_uri}}}') else tag.split('}')[-1]
        return order_list.index(local_name) if local_name in order_list else len(order_list)
        
    children = list(parent)
    for child in children: parent.remove(child)
    children.sort(key=key_func)
    for child in children: parent.append(child)

def build_abstract_num(abstract_id, levels):
    """Build an abstractNum element from level definitions."""
    nsid = f'{abstract_id:08X}'
    tmpl = f'{abstract_id + 1:08X}'

    abstract = ET.Element(f'{{{W_NS}}}abstractNum')
    abstract.set(f'{{{W_NS}}}abstractNumId', str(abstract_id))

    nsid_elem = ET.SubElement(abstract, f'{{{W_NS}}}nsid')
    nsid_elem.set(f'{{{W_NS}}}val', nsid)

    mlt = ET.SubElement(abstract, f'{{{W_NS}}}multiLevelType')
    mlt.set(f'{{{W_NS}}}val', 'multilevel')

    tmpl_elem = ET.SubElement(abstract, f'{{{W_NS}}}tmpl')
    tmpl_elem.set(f'{{{W_NS}}}val', tmpl)

    for i, level_def in enumerate(levels):
        fmt = level_def[0]
        text = level_def[1]
        jc = level_def[2]
        left = level_def[3]
        hanging = level_def[4]
        font = level_def[5] if len(level_def) > 5 else None

        lvl = ET.SubElement(abstract, f'{{{W_NS}}}lvl')
        lvl.set(f'{{{W_NS}}}ilvl', str(i))

        start = ET.SubElement(lvl, f'{{{W_NS}}}start')
        start.set(f'{{{W_NS}}}val', '1')

        numfmt = ET.SubElement(lvl, f'{{{W_NS}}}numFmt')
        numfmt.set(f'{{{W_NS}}}val', fmt)

        lvltext = ET.SubElement(lvl, f'{{{W_NS}}}lvlText')
        lvltext.set(f'{{{W_NS}}}val', text)

        lvljc = ET.SubElement(lvl, f'{{{W_NS}}}lvlJc')
        lvljc.set(f'{{{W_NS}}}val', jc)

        # Space suffix to eliminate big gaps after numbers
        suff = ET.SubElement(lvl, f'{{{W_NS}}}suff')
        suff.set(f'{{{W_NS}}}val', 'space')

        pPr = ET.SubElement(lvl, f'{{{W_NS}}}pPr')
        ind = ET.SubElement(pPr, f'{{{W_NS}}}ind')
        ind.set(f'{{{W_NS}}}left', str(left))
        ind.set(f'{{{W_NS}}}hanging', str(hanging))

        if font:
            rPr = ET.SubElement(lvl, f'{{{W_NS}}}rPr')
            rFonts = ET.SubElement(rPr, f'{{{W_NS}}}rFonts')
            rFonts.set(f'{{{W_NS}}}ascii', font)
            rFonts.set(f'{{{W_NS}}}hAnsi', font)
            rFonts.set(f'{{{W_NS}}}hint', 'default')

        sort_element_children(lvl, LVL_ORDER)

    return abstract

def build_num(num_id, abstract_id):
    """Build a num element referencing an abstractNum."""
    num = ET.Element(f'{{{W_NS}}}num')
    num.set(f'{{{W_NS}}}numId', str(num_id))
    abstract_ref = ET.SubElement(num, f'{{{W_NS}}}abstractNumId')
    abstract_ref.set(f'{{{W_NS}}}val', str(abstract_id))
    return num

def ensure_content_type(unpacked_dir):
    """Ensure [Content_Types].xml has the numbering override."""
    ct_path = os.path.join(unpacked_dir, '[Content_Types].xml')
    if not os.path.exists(ct_path):
        print(f"Warning: {ct_path} not found")
        return

    tree = ET.parse(ct_path)
    root = tree.getroot()

    numbering_ct = 'application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml'
    for override in root.findall(f'{{{CT_NS}}}Override'):
        if override.get('PartName') == '/word/numbering.xml':
            return  # Already exists

    override = ET.SubElement(root, f'{{{CT_NS}}}Override')
    override.set('PartName', '/word/numbering.xml')
    override.set('ContentType', numbering_ct)
    tree.write(ct_path, encoding='utf-8', xml_declaration=True)
    print("  Updated [Content_Types].xml")

def ensure_relationship(unpacked_dir):
    """Ensure word/_rels/document.xml.rels links to numbering.xml."""
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')
    if not os.path.exists(rels_path):
        print(f"Warning: {rels_path} not found")
        return

    tree = ET.parse(rels_path)
    root = tree.getroot()

    for rel in root.findall(f'{{{REL_NS}}}Relationship'):
        if rel.get('Type') == NUM_REL_TYPE:
            return  # Already exists

    # Find next rId
    existing_ids = []
    for rel in root.findall(f'{{{REL_NS}}}Relationship'):
        rid = rel.get('Id', '')
        if rid.startswith('rId'):
            try:
                existing_ids.append(int(rid[3:]))
            except ValueError:
                pass
    next_id = max(existing_ids) + 1 if existing_ids else 1

    new_rel = ET.SubElement(root, f'{{{REL_NS}}}Relationship')
    new_rel.set('Id', f'rId{next_id}')
    new_rel.set('Type', NUM_REL_TYPE)
    new_rel.set('Target', 'numbering.xml')
    tree.write(rels_path, encoding='utf-8', xml_declaration=True)
    print(f"  Updated document.xml.rels (rId{next_id})")

def inject_preset(unpacked_dir, preset_name, target_num_id):
    numbering_path = os.path.join(unpacked_dir, 'word', 'numbering.xml')
    os.makedirs(os.path.dirname(numbering_path), exist_ok=True)

    # Register namespace
    if hasattr(ET, 'register_namespace'):
        ET.register_namespace('w', W_NS)
        ET.register_namespace('w15', W15_NS)

    if os.path.exists(numbering_path):
        tree = ET.parse(numbering_path)
        root = tree.getroot()
    else:
        root = ET.Element(f'{{{W_NS}}}numbering')
        tree = ET.ElementTree(root)

    # Find if target_num_id already exists, and if so, remove it
    for num in list(root.findall(f'{{{W_NS}}}num')):
        if num.get(f'{{{W_NS}}}numId') == str(target_num_id):
            pref = num.find(f'{{{W_NS}}}abstractNumId')
            if pref is not None:
                ab_id = pref.get(f'{{{W_NS}}}val')
                for ab in list(root.findall(f'{{{W_NS}}}abstractNum')):
                    if ab.get(f'{{{W_NS}}}abstractNumId') == ab_id:
                        root.remove(ab)
            root.remove(num)

    # Find max abstractNumId to create a new one
    max_abstract = -1
    for an in root.findall(f'{{{W_NS}}}abstractNum'):
        aid = int(an.get(f'{{{W_NS}}}abstractNumId', '-1'))
        max_abstract = max(max_abstract, aid)
    new_abstract_id = max_abstract + 1

    # Build and inject
    abstract_elem = build_abstract_num(new_abstract_id, PRESETS[preset_name]['levels'])
    num_elem = build_num(target_num_id, new_abstract_id)

    # Insert abstractNum before any num elements
    nums = root.findall(f'{{{W_NS}}}num')
    if nums:
        root.insert(list(root).index(nums[0]), abstract_elem)
    else:
        root.append(abstract_elem)
    root.append(num_elem)

    # Save
    tree.write(numbering_path, encoding='utf-8', xml_declaration=True)
    print(f"Injected preset '{preset_name}' as numId={target_num_id}, abstractNumId={new_abstract_id}")

    # Ensure supporting files
    ensure_content_type(unpacked_dir)
    ensure_relationship(unpacked_dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python add_numbering_preset.py <unpacked_dir>")
        sys.exit(1)
    unpacked_dir = sys.argv[1]
    inject_preset(unpacked_dir, 'thesis-heading', 76)
    inject_preset(unpacked_dir, 'thesis', 77)
