import pypdf
import os

def search_pdf(pdf_path, keywords):
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found")
        return
        
    print(f"\nSearching in {os.path.basename(pdf_path)}...")
    reader = pypdf.PdfReader(pdf_path)
    print(f"Total pages: {len(reader.pages)}")
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
            
        found_keys = []
        for key in keywords:
            if key.lower() in text.lower():
                found_keys.append(key)
                
        if found_keys:
            print(f"\n--- Page {idx + 1} matches: {found_keys} ---")
            lines = text.split('\n')
            for line in lines:
                for key in keywords:
                    if key.lower() in line.lower():
                        print(f"  {line[:120]}")
                        break

if __name__ == '__main__':
    keywords = ["proyek", "font", "margin", "kertas", "spasi", "tabel", "gambar", "bab ", "lampiran", "judul"]
    search_pdf("Pedoman-TA-FIK-2025_6.pdf", keywords)
