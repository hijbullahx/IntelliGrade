import docx

src_path = r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx'
doc = docx.Document(src_path)

# Let's inspect P[43], P[67], P[95], P[181]
p43 = doc.paragraphs[43]
p67 = doc.paragraphs[67]
p95 = doc.paragraphs[95]
p181 = doc.paragraphs[181]

print("P[43] text:", repr(p43.text))
print("P[44] text:", repr(doc.paragraphs[44].text))
print("P[67] text:", repr(p67.text))
print("P[95] text:", repr(p95.text))
print("P[181] text:", repr(p181.text))
print("P[183] text:", repr(doc.paragraphs[183].text))

# Move sectPr from P[67] to P[43]
sectPr_67 = p67._p.xpath('./w:pPr/w:sectPr')[0]
p67._p.pPr.remove(sectPr_67)
p43._p.get_or_add_pPr().append(sectPr_67)

# Remove sectPr from P[95]
sectPr_95 = p95._p.xpath('./w:pPr/w:sectPr')[0]
p95._p.pPr.remove(sectPr_95)

test_out = r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections.docx'
doc.save(test_out)

doc2 = docx.Document(test_out)
print(f"Total sections after move: {len(doc2.sections)}")
for i, s in enumerate(doc2.sections):
    print(f"Section {i}: start_type={s.start_type}")

