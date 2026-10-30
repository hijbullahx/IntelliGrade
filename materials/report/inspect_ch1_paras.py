import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.docx')
for i in range(178, 188):
    p = doc.paragraphs[i]
    sect = p._p.xpath('./w:pPr/w:sectPr')
    print(f"P[{i}]: sectPr={len(sect)}, text='{p.text}'")

