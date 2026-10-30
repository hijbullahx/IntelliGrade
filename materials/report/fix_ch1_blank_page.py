import docx

dst_v3 = r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v3).docx'
doc = docx.Document(dst_v3)

ch1_p = None
for i, p in enumerate(doc.paragraphs):
    if p.text.strip().startswith("Chapter 1."):
        ch1_p = p
        print(f"P[{i}]: text='{p.text}', page_break_before={p.paragraph_format.page_break_before}")
        # Turn off page_break_before since section break starts on new page
        p.paragraph_format.page_break_before = False
        # Also check preceding paragraph
        prev_p = doc.paragraphs[i-1]
        print(f"P[{i-1}]: text='{prev_p.text}', page_break_before={prev_p.paragraph_format.page_break_before}")
        break

doc.save(dst_v3)
print("Updated Chapter 1 page_break_before to False.")

