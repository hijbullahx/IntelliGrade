import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

test_path = r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections.docx'
doc = docx.Document(test_path)

# Section 0
sec0 = doc.sections[0]
sec0.header.is_linked_to_previous = False
sec0.footer.is_linked_to_previous = False
for p in sec0.header.paragraphs:
    p.text = ''
for p in sec0.footer.paragraphs:
    p.text = ''

# Section 1
sec1 = doc.sections[1]
sec1.header.is_linked_to_previous = False
sec1.footer.is_linked_to_previous = False
for p in sec1.header.paragraphs:
    p.text = ''
# Clear footer and add page field
f1 = sec1.footer.paragraphs[0]
f1.text = ''
f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
f1._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
for p in sec1.footer.paragraphs[1:]:
    p.text = ''

# Section 1 pgNumType: lowerRoman starting at 3
sectPr1 = sec1._sectPr
for pnt in sectPr1.xpath('./w:pgNumType'):
    sectPr1.remove(pnt)
pgNumType1 = OxmlElement('w:pgNumType')
pgNumType1.set(qn('w:fmt'), 'lowerRoman')
pgNumType1.set(qn('w:start'), '3')
# In sectPr, pgNumType must be inserted before cols if cols exists
cols1 = sectPr1.xpath('./w:cols')
if cols1:
    cols1[0].addprevious(pgNumType1)
else:
    sectPr1.append(pgNumType1)

# Section 2
sec2 = doc.sections[2]
sec2.header.is_linked_to_previous = False
sec2.footer.is_linked_to_previous = False
for p in sec2.header.paragraphs:
    p.text = ''
f2 = sec2.footer.paragraphs[0]
f2.text = ''
f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
f2._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
for p in sec2.footer.paragraphs[1:]:
    p.text = ''

# Section 2 pgNumType: decimal starting at 1
sectPr2 = sec2._sectPr
for pnt in sectPr2.xpath('./w:pgNumType'):
    sectPr2.remove(pnt)
pgNumType2 = OxmlElement('w:pgNumType')
pgNumType2.set(qn('w:fmt'), 'decimal')
pgNumType2.set(qn('w:start'), '1')
cols2 = sectPr2.xpath('./w:cols')
if cols2:
    cols2[0].addprevious(pgNumType2)
else:
    sectPr2.append(pgNumType2)

out_path = r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.docx'
doc.save(out_path)
print("Saved numbered sections docx.")

