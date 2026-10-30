import fitz

pdf = fitz.open(r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.pdf')
for pno in range(14, 20):
    print(f"=== PAGE {pno+1} ===")
    print(pdf[pno].get_text()[:400])

