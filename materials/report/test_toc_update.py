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
    print("Opened doc.")
    print("TOC count:", doc.TablesOfContents.Count)
    if doc.TablesOfContents.Count > 0:
        toc = doc.TablesOfContents(1)
        toc.Update()
        print("Updated TOC!")
        print("TOC Range text preview:")
        lines = toc.Range.Text.split('\r')
        for l in lines[:20]:
            if l.strip():
                print("  ", l.strip())
    doc.Save()
    doc.Close(False)
finally:
    word.Quit()

