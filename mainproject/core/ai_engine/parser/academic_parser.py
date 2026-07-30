import re
from typing import Dict, Any, List
from core.ai_engine.layout.academic_layout import AcademicLayoutAnalyzer

class AcademicDocumentParser:
    """
    Central Academic Document Parser for IntelliGrade.
    Transforms raw OCR output into clean, validated Academic JSON schema
    BEFORE passing structured data to the LLM or Database models.
    """

    def __init__(self):
        self.layout_analyzer = AcademicLayoutAnalyzer()

    def parse_document(self, raw_ocr_text: str) -> Dict[str, Any]:
        """
        Parses raw OCR text into clean structured JSON.
        """
        if not raw_ocr_text or not raw_ocr_text.strip():
            return {
                "header": {},
                "questions": [],
                "tables": [],
                "copo_mapping": [],
                "equations": [],
                "raw_clean_text": ""
            }

        # Step 1: Layout Analysis & Structural Bounding Segmentation
        layout = self.layout_analyzer.analyze_layout(raw_ocr_text)

        # Step 2: Clean & Normalize Header Metadata
        header_text = " ".join(layout.get('header', []))
        university_match = re.search(r'(International University [^\n,]+|IUBAT|[A-Za-z\s]+ University)', header_text, re.IGNORECASE)
        dept_match = re.search(r'Department of ([A-Za-z\s&]+)', header_text, re.IGNORECASE)
        course_match = re.search(r'([A-Z]{2,4}\s*\d{3,4})', raw_ocr_text)
        exam_match = re.search(r'(Final Examination|Midterm Examination|Quiz \d+|Assignment)', raw_ocr_text, re.IGNORECASE)

        header_json = {
            "university": university_match.group(0).strip() if university_match else "IUBAT",
            "department": dept_match.group(1).strip() if dept_match else "Computer Science & Engineering",
            "course_code": course_match.group(1).upper().strip() if course_match else None,
            "exam_type": exam_match.group(0).strip() if exam_match else "Final Examination"
        }

        # Step 3: Parse Question Blocks into Clean JSON
        parsed_questions = []
        raw_blocks = layout.get('question_blocks', [])

        for b in raw_blocks:
            q_num = b.get('question_number', 'Q1')
            content = b.get('content', '')

            # Extract marks
            m_match = re.search(r'\[(\d+(?:\.\d+)?)\s*Marks?\]|(\d+)\s*Marks', content, re.IGNORECASE)
            marks = float(m_match.group(1) or m_match.group(2)) if m_match else 10.0

            # Extract Bloom verb
            verb_match = re.search(r'\b(Explain|Describe|Calculate|Compute|Design|Analyze|Compare|Contrast|Solve|Define)\b', content, re.IGNORECASE)
            c_verb = verb_match.group(0).capitalize() if verb_match else "Explain"

            # Deduce Bloom Level
            bloom = "Understand"
            if c_verb in ["Calculate", "Compute", "Solve"]:
                bloom = "Apply"
            elif c_verb in ["Design", "Develop"]:
                bloom = "Create"
            elif c_verb in ["Compare", "Analyze", "Contrast"]:
                bloom = "Analyze"

            parsed_questions.append({
                "question_number": q_num,
                "prompt_text": content.strip(),
                "allocated_marks": marks,
                "command_verbs": [c_verb],
                "bloom_level": bloom,
                "co_mapping": "CO1",
                "po_mapping": ["PO1"]
            })

        # Return Clean Academic JSON
        return {
            "header": header_json,
            "questions": parsed_questions,
            "tables": layout.get('tables', []),
            "copo_mapping": layout.get('copo_tables', []),
            "equations": layout.get('equations', []),
            "code_blocks": layout.get('code_blocks', []),
            "page_count": len(layout.get('page_numbers', [1])),
            "raw_clean_text": raw_ocr_text.strip()
        }
