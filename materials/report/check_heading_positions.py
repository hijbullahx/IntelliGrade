import fitz

pdf = fitz.open(r'D:\Projects\IntelliGrade\Materials\report\Practicum_Soft_Report_Template_DAS(v3).pdf')
headings = [
    "Letter of Transmittal",
    "Organization’s Certificate",
    "Student’s Declaration",
    "Supervisor’s Certification",
    "Abstract",
    "Acknowledgments",
    "Table of Contents",
    "List of Figures",
    "List of Tables",
    "Chapter 1. Introduction",
    "Chapter 2.",
    "Chapter 3.",
    "Chapter 4.",
    "Chapter 5.",
    "Chapter 6.",
    "Chapter 7.",
    "Chapter 8.",
    "Chapter 9.",
    "Chapter 10.",
    "References",
    "Plagiarism Report"
]

for pno, page in enumerate(pdf):
    txt = page.get_text()
    for h in headings:
        if h in txt or h.replace("’", "") in txt:
            # find bbox of heading
            for b in page.get_text("blocks"):
                if h in b[4] or h.replace("’", "") in b[4]:
                    print(f"Page {pno+1}: '{h}' at y={b[1]:.1f}")

