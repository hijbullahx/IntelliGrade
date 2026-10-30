import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()
p = doc.add_paragraph("Test paragraph")
# To add a field to a paragraph:
# runs inside the paragraph:
fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))

r1 = p.add_run()._r
r1.append(fldChar1)
r2 = p.add_run()._r
r2.append(instrText)
r3 = p.add_run()._r
r3.append(fldChar2)
r4 = p.add_run()._r
r4.append(fldChar3)

doc.save(r'D:\Projects\IntelliGrade\Materials\report\test_fld.docx')
print("Saved test_fld.docx successfully")

