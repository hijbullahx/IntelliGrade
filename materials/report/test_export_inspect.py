import win32com.client as win32
import fitz, os

pdf_path = os.path.abspath(r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.pdf')
doc_path = os.path.abspath(r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.docx')

word = win32.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False
doc = word.Documents.Open(doc_path)
doc.ExportAsFixedFormat(pdf_path, 17) # 17 = wdExportFormatPDF
doc.Close(False)
word.Quit()
print('Exported to PDF!')

pdf = fitz.open(pdf_path)
print('PDF pages count:', len(pdf))
for pno in [0, 1, 2, 3, 4, 15, 16, 17, 18, 19]:
    txt = pdf[pno].get_text()
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    first_line = lines[0] if lines else 'EMPTY'
    last_line = lines[-1] if lines else 'EMPTY'
    print(f'Page {pno+1}: bottom="{last_line}", top="{first_line[:40]}"')

