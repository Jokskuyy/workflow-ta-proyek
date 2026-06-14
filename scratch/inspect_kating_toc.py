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
    # extract first 12 pages
    extract_pages("Tugas Akhir_Abimanyu Damarjati_2110511110.pdf", range(0, 12), "scratch/kating_toc.txt")
