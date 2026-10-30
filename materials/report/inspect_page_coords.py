import fitz

pdf = fitz.open(r'D:\Projects\IntelliGrade\Materials\report\test_clean_sections_numbered.pdf')
print("=== Page 17 (0-indexed 16) blocks ===")
p17 = pdf[16]
for b in p17.get_text("blocks"):
    print(f"bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) text: {repr(b[4].strip())}")

print("\n=== Page 18 (0-indexed 17) blocks ===")
p18 = pdf[17]
for b in p18.get_text("blocks"):
    print(f"bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) text: {repr(b[4].strip())}")

