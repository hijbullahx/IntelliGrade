import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')

print("Paragraphs with sectPr:")
for i, p in enumerate(doc.paragraphs):
    sectPr = p._p.xpath('./w:pPr/w:sectPr')
    if sectPr:
        print(f"P[{i}]: text='{p.text[:40]}'")
print("Body sectPr:", doc._body._element.xpath('./w:sectPr') is not None)

