# IntelliGrade — Academic & Technical Glossary

**Document Version:** 3.5.0 (Enterprise Academic Edition)  
**Last Updated:** August 29, 2026  
**Auditor:** Principal Enterprise Systems Architect  

---

## 1. Academic & Accreditation Terminology

| Term | Definition & Context in IntelliGrade |
| :--- | :--- |
| **Outcome-Based Education (OBE)** | An educational theory and accreditation framework focusing on measurable student learning outcomes rather than instructional inputs. |
| **Course Outcome (CO)** | Specific, measurable competencies a student must demonstrate upon completing a course (e.g. `CO1: Understand matrix operations`, `CO2: Apply graph algorithms`). |
| **Program Outcome (PO)** | Broad professional skills and engineering graduate attributes defined by accreditation bodies like BAETE (e.g. `PO1: Engineering Knowledge`, `PO2: Problem Analysis`, `PO3: Design/Development`). |
| **Bloom's Taxonomy** | Hierarchical classification of cognitive educational objectives: *Remember, Understand, Apply, Analyze, Evaluate, Create*. |
| **Knowledge Profile (KP)** | Definitions of engineering science and mathematical depth required for complex engineering analysis (`KP1` to `KP8`). |
| **Complex Engineering Problem (CEP)** | Problems characterized by in-depth engineering fundamentals, wide-ranging conflicting issues, or lack of obvious solutions (`CEP1` to `CEP7`). |
| **Complex Engineering Activity (CEA)** | Engineering activities involving diverse resources, significant consequences, and innovative approaches (`CEA1` to `CEA5`). |
| **Course Tabulation Sheet** | The official university grade register compiling student scores across Class Tests, Midterms, Finals, Assignments, Attendance, and OBE attainments. |
| **Continuous Quality Improvement (CQI)** | An iterative quality assurance methodology where faculty analyze class-wide OBE attainments to improve syllabus, pedagogy, and assessment rubrics. |
| **Grading Rubric** | A scoring guide outlining explicit criteria, mark distributions, expected keywords, model answers, and deductions for student evaluation. |

---

## 2. Technical & Architectural Terminology

| Term | Definition & Context in IntelliGrade |
| :--- | :--- |
| **PyMuPDF (`fitz`)** | High-performance C-based Python library used to parse PDF font glyph maps and rasterize pages at 300 DPI high resolution. |
| **EasyOCR** | PyTorch-powered deep learning Optical Character Recognition engine specialized in recognizing handwritten text and complex scripts. |
| **PyTesseract** | Python wrapper for Google's Tesseract-OCR engine, used as the primary high-speed OCR extractor for printed examination documents. |
| **Bounding Box (BBox)** | A set of rectangular coordinate tuples (`[ymin, xmin, ymax, xmax]` or `[xmin, ymin, xmax, ymax]`) demarcating the spatial location of words, questions, figures, or answer regions. |
| **TaskRouter** | IntelliGrade's intelligent routing component that inspects task types (`ANSWER_VISUAL_READ`, `ANSWER_GRADING`, `ROUTINE_PARSE`) to select the optimal AI provider. |
| **FailoverAIProvider** | Resilient multi-model orchestrator that manages sequential fallback (Local Vision $\rightarrow$ Groq $\rightarrow$ OpenRouter $\rightarrow$ Gemini $\rightarrow$ OpenAI) upon errors or timeouts. |
| **ProviderHealthTracker** | Centralized in-memory registry monitoring HTTP 429 rate limits, token quotas, and applying exponential backoff cooldowns. |
| **LaTeX Regex Repair** | Sanitization filter in `BaseAIProvider` escaping invalid backslashes in mathematical formulas before JSON parsing (`re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', text)`). |
| **openpyxl** | Python library utilized to generate, populate, and format the official 8-sheet OBE Excel workbooks with live formula compilation. |
| **Human-in-the-Loop (HITL)** | Design paradigm ensuring AI serves only as an assistive advisor, requiring explicit teacher review and approval before grades are finalized. |
