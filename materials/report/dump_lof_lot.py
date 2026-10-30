import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')

print("=== All LOF paragraphs ===")
for j in range(108, 140):
    t = doc.paragraphs[j].text.strip()
    if t:
        print(f"  P[{j}]: {t}")

print("\n=== All LOT paragraphs ===")
for j in range(141, 182):
    t = doc.paragraphs[j].text.strip()
    if t:
        print(f"  P[{j}]: {t}")

