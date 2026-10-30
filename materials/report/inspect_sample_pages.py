import fitz

doc = fitz.open(r'D:\Projects\IntelliGrade\Materials\report\A_Practicum Report_Md Minhazul Islam.pdf(Sample).pdf')
for pno in [9, 10, 11, 12, 13, 14, 15, 16, 17]: # 0-indexed
    print(f'=== PAGE {pno+1} ===')
    txt = doc[pno].get_text()
    for line in txt.split('\n')[:15]:
        print('  ', line)

