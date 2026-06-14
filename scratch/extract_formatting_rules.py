import pypdf

def extract_formatting_rules(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    keywords = ["margin", "spasi", "font", "kertas", "ukuran", "tabel ", "gambar ", "penomoran"]
    
    print("Extracting formatting details from guidelines...")
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
            
        lines = text.split('\n')
        for line in lines:
            # Check if any keyword matches and print the line with context
            for kw in keywords:
                if kw.lower() in line.lower():
                    # We want to print lines that contain details like 4 cm, 3 cm, Times New Roman, etc.
                    if any(c in line for c in ["3", "4", "1,5", "1.5", "12", "14", "Times", "A4"]):
                        print(f"Page {idx+1}: {line.strip()}")
                        break

if __name__ == '__main__':
    extract_formatting_rules("Pedoman-TA-FIK-2025_6.pdf")
