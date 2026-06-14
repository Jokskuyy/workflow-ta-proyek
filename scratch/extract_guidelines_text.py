import pypdf

def extract_pages(pdf_path, pages, output_path):
    reader = pypdf.PdfReader(pdf_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for p_num in pages:
            if p_num < len(reader.pages):
                page = reader.pages[p_num]
                text = page.extract_text()
                f.write(f"=== PAGE {p_num + 1} ===\n")
                f.write(text)
                f.write("\n\n")
    print(f"Extracted pages {pages} to {output_path}")

if __name__ == '__main__':
    # pages are 0-indexed: page 26 is index 25, page 27 is index 26, etc.
    extract_pages("Pedoman-TA-FIK-2025_6.pdf", range(24, 30), "scratch/guidelines_outline.txt")
