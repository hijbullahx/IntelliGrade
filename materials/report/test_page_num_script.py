import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()
# Section 1 - cover
doc.add_paragraph('Section 1 - Cover page')
# Section 2 - front matter
sec2 = doc.add_section()
doc.add_paragraph('Section 2 - Letter of transmittal')
sectPr2 = sec2._sectPr
pgNumType2 = OxmlElement('w:pgNumType')
pgNumType2.set(qn('w:fmt'), 'lowerRoman')
pgNumType2.set(qn('w:start'), '3')
sectPr2.append(pgNumType2)
# Add footer to sec2
f_p = sec2.footer.paragraphs[0]
f_p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
f_p._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))

# Section 3 - body
sec3 = doc.add_section()
doc.add_paragraph('Section 3 - Chapter 1')
sectPr3 = sec3._sectPr
pgNumType3 = OxmlElement('w:pgNumType')
pgNumType3.set(qn('w:fmt'), 'decimal')
pgNumType3.set(qn('w:start'), '1')
sectPr3.append(pgNumType3)
# Add footer to sec3
f_p3 = sec3.footer.paragraphs[0]
f_p3.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
f_p3._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))

test_path = r'D:\Projects\IntelliGrade\Materials\report\test_xml_pagenums.docx'
doc.save(test_path)
print('Saved test docx!')

import win32com.client, pythoncom
pythoncom.CoInitialize()
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = False
wdoc = word.Documents.Open(test_path)
print('Word opened test docx! Pages:', wdoc.ComputeStatistics(2))
for i in range(1, wdoc.Sections.Count+1):
    s = wdoc.Sections(i)
    ftr_text = s.Footers(1).Range.Text.strip()
    print(f'Sec {i} footer text:', repr(ftr_text))
wdoc.Close(False)
word.Quit()
print('Word test completed successfully!')

