import win32com.client
import os

def main():
    doc_path = os.path.abspath("Tugas_Akhir_Formatted.docx")
    if not os.path.exists(doc_path):
        print(f"Error: {doc_path} not found")
        return
        
    print(f"Opening {doc_path} in Word to check page numbers...")
    word = None
    doc = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(doc_path)
        
        print("\n--- Document Heading Page Numbers ---")
        for i, para in enumerate(doc.Paragraphs):
            text = para.Range.Text.strip()
            if not text:
                continue
                
            # Information(1) returns the page number (wdActiveEndAdjustedPageNumber)
            try:
                page_num = para.Range.Information(1)
            except Exception as e:
                page_num = "Error"
                
            # Check if this paragraph is a heading style or contains heading text
            style_name = para.Style.NameLocal
            
            is_interesting = (
                "Heading" in style_name or
                "Judul" in style_name or
                any(kw in text.upper() for kw in ["DAFTAR", "BAB", "KATA PENGANTAR", "ABSTRAK"])
            )
            
            if is_interesting:
                print(f"Para #{i:03d} | Page {page_num} | Style: {style_name:<20} | Text: '{text[:80]}'")
                
    except Exception as e:
        print("Error:", e)
    finally:
        if doc:
            doc.Close(SaveChanges=0)
        if word:
            word.Quit()

if __name__ == '__main__':
    main()
