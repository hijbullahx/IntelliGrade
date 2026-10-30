import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')
for i in range(40, 185):
    txt = doc.paragraphs[i].text.strip()
    if txt and (doc.paragraphs[i].style.name.startswith('Heading') or any(k in txt for k in ['Transmittal', 'Certificate', 'Declaration', 'Abstract', 'Acknowledgments', 'Table of Contents', 'List of Figures', 'List of Tables', 'Chapter 1'])):
        print(f'P[{i}]: "{txt}" (style={doc.paragraphs[i].style.name})')

