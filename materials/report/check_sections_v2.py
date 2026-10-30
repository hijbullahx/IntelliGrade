import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')
print(f"Total sections: {len(doc.sections)}")
for i, s in enumerate(doc.sections):
    print(f"\n--- Section {i} ---")
    print(f"Start type: {s.start_type}")
    print(f"Page width: {s.page_width}, height: {s.page_height}")
    print(f"Top margin: {s.top_margin}, bottom margin: {s.bottom_margin}")
    print(f"Left margin: {s.left_margin}, right margin: {s.right_margin}")
    print(f"Header linked: {s.header.is_linked_to_previous}")
    print(f"Footer linked: {s.footer.is_linked_to_previous}")
    for p in s.header.paragraphs:
        if p.text.strip():
            print(f"  Header text: {p.text.strip()}")
    for p in s.footer.paragraphs:
        if p.text.strip():
            print(f"  Footer text: {p.text.strip()}")

