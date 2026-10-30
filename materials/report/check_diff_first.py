import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.docx')
for i, s in enumerate(doc.sections):
    print(f"=== Section {i} ===")
    print(f"different_first_page_header_footer: {s.different_first_page_header_footer}")
    print("Normal footer:", repr(s.footer.paragraphs[0].text if s.footer.paragraphs else 'None'))
    print("First page footer linked:", s.first_page_footer.is_linked_to_previous)
    print("First page footer text:", repr(s.first_page_footer.paragraphs[0].text if s.first_page_footer.paragraphs else 'None'))

