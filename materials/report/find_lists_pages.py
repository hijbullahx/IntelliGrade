import fitz

pdf = fitz.open(r'D:\Projects\IntelliGrade\Materials\report\test_clean_fixed_first.pdf')
for pno in range(len(pdf)):
    txt = pdf[pno].get_text()
    if 'LIST OF FIGURES' in txt.upper() or 'LIST OF TABLES' in txt.upper():
        footer = [b[4].strip() for b in pdf[pno].get_text('blocks') if b[1] > 720 and b[4].strip()]
        first_line = txt.strip().split('\n')[0]
        print(f"Page {pno+1}: footer={footer}, title='{first_line}'")

