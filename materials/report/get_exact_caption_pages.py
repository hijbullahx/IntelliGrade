import win32com.client as win32
import pythoncom
import os

pythoncom.CoInitialize()
word = win32.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False

try:
    doc_path = os.path.abspath(r'D:\Projects\IntelliGrade\Materials\report\test_clean_fixed_first.docx')
    doc = word.Documents.Open(doc_path)
    
    figures = []
    tables = []
    
    # Iterate through paragraphs in Section 3 (the body section)
    # Sec 3 is doc.Sections(3)
    sec3 = doc.Sections(3)
    for p in sec3.Range.Paragraphs:
        t = p.Range.Text.strip()
        if t.startswith("Figure ") and len(t) > 10:
            pg = p.Range.Information(1) # wdActiveEndAdjustedPageNumber
            figures.append((t, pg))
        elif t.startswith("Table ") and len(t) > 9:
            pg = p.Range.Information(1)
            tables.append((t, pg))
            
    print(f"Found {len(figures)} Figures in Section 3:")
    for f in figures[:5]:
        print(f"  {f[0]} -> Page {f[1]}")
    print(f"Found {len(tables)} Tables in Section 3:")
    for t in tables[:5]:
        print(f"  {t[0]} -> Page {t[1]}")
        
    doc.Close(False)
finally:
    word.Quit()

