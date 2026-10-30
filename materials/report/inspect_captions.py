import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')
print('Total paragraphs:', len(doc.paragraphs))

current_heading = 'None'
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if p.style.name.startswith('Heading') or txt.startswith('Chapter'):
        current_heading = txt
    if (txt.startswith('Table ') or txt.startswith('Table\t') or txt.startswith('Figure ') or txt.startswith('Figure\t')) and i > 180:
        print(f'P[{i}] (under {current_heading[:35]}): {txt}')

