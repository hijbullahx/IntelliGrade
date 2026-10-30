import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

test_path = r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.docx'
doc = docx.Document(test_path)

for i, s in enumerate(doc.sections):
    s.different_first_page_header_footer = False
    s.header.is_linked_to_previous = False
    s.footer.is_linked_to_previous = False
    for p in s.header.paragraphs:
        p.text = ''
    if i == 0:
        for p in s.footer.paragraphs:
            p.text = ''
    else:
        f = s.footer.paragraphs[0]
        f.text = ''
        f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        f._p.append(parse_xml('<w:fldSimple ' + nsdecls('w') + ' w:instr="PAGE"/>'))
        for p in s.footer.paragraphs[1:]:
            p.text = ''

out_path = r'D:\Projects\IntelliGrade\Materials\report\test_clean_fixed_first.docx'
doc.save(out_path)
print("Saved fixed docx!")

