import win32com.client as win32
import os

word = win32.Dispatch('Word.Application')
word.Visible = False
try:
    file_path = os.path.abspath(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')
    doc = word.Documents.Open(file_path, ReadOnly=True)
    print("Document opened successfully.")
    print("TablesOfContents count:", doc.TablesOfContents.Count)
    print("Fields count:", doc.Fields.Count)
    doc.Close(False)
finally:
    word.Quit()
print("Done")

