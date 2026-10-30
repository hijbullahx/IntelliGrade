import docx

doc = docx.Document(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v2).docx')

lof_idx = None
lot_idx = None
ch1_idx = None

for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t == "List of Figures":
        lof_idx = i
    elif t == "List of Tables":
        lot_idx = i
    elif "Chapter 1." in t and ch1_idx is None:
        ch1_idx = i

print(f"List of Figures: P[{lof_idx}]")
print(f"List of Tables: P[{lot_idx}]")
print(f"Chapter 1: P[{ch1_idx}]")

print(f"\nBetween LOF and LOT (count={lot_idx - lof_idx - 1}):")
for j in range(lof_idx + 1, min(lof_idx + 6, lot_idx)):
    print(f"  P[{j}]: {doc.paragraphs[j].text}")

print(f"\nBetween LOT and Ch1 (count={ch1_idx - lot_idx - 1}):")
for j in range(lot_idx + 1, min(lot_idx + 6, ch1_idx)):
    print(f"  P[{j}]: {doc.paragraphs[j].text}")

