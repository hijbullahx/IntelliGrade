import re
from typing import Dict, Any, List

class AcademicLayoutAnalyzer:
    """
    Analyzes document layout structure for academic examination papers & scripts.
    Identifies: Header, Footer, Question blocks, Figures, Tables, Matrices, Code blocks,
    Equations, Captions, CO/PO table, Mark allocations, Page numbers, and Document sections.
    """

    def analyze_layout(self, text_or_ocr: str) -> Dict[str, Any]:
        lines = [line.strip() for line in text_or_ocr.split('\n') if line.strip()]

        headers = []
        footers = []
        question_blocks = []
        tables = []
        figures = []
        equations = []
        code_blocks = []
        copo_tables = []
        mark_allocations = []
        page_numbers = []

        current_block = []
        current_q_num = None

        for line in lines:
            # Detect Page Number
            if re.match(r'^(?:Page\s*\d+|\d+\s*of\s*\d+)$', line, re.IGNORECASE):
                page_numbers.append(line)
                continue

            # Detect Header (University, Department, Exam title)
            if any(k in line.lower() for k in ['university', 'department', 'faculty of', 'final examination', 'midterm examination', 'time allowed']):
                headers.append(line)
                continue

            # Detect Footer
            if any(k in line.lower() for k in ['turn over', 'good luck', 'end of paper', 'page']):
                footers.append(line)
                continue

            # Detect CO/PO Table
            if any(k in line.lower() for k in ['co mapping', 'po mapping', 'course outcome', 'program outcome']):
                copo_tables.append(line)
                continue

            # Detect Mark Allocations
            marks_match = re.search(r'\[(\d+(?:\.\d+)?)\s*Marks?\]|(\d+)\s*Marks', line, re.IGNORECASE)
            if marks_match:
                m_val = marks_match.group(1) or marks_match.group(2)
                mark_allocations.append({"line": line, "marks": float(m_val)})

            # Detect Question Number (Q1, Q1 (a), Question 2)
            q_match = re.match(r'^(?:Q\d+|Question\s*\d+)(?:\s*\([a-z\d]+\))?', line, re.IGNORECASE)
            if q_match:
                if current_q_num and current_block:
                    question_blocks.append({
                        "question_number": current_q_num,
                        "content": "\n".join(current_block)
                    })
                current_q_num = q_match.group(0)
                current_block = [line]
                continue

            # Detect Equation or Math
            if any(sym in line for sym in ['=', '∫', '∑', '√', '±', 'λ', 'θ', 'lim']) or re.search(r'[a-z]\s*=\s*[0-9]', line):
                equations.append(line)

            # Detect Code block
            if any(line.startswith(kw) for kw in ['def ', 'class ', 'import ', 'for(', 'while(', 'int ', 'void ', '#include']):
                code_blocks.append(line)

            # Detect Figure or Diagram reference
            if re.search(r'(?:Figure|Fig\.|Diagram)\s*\d+', line, re.IGNORECASE):
                figures.append(line)

            # Detect Table structure
            if '|' in line or '\t' in line or re.search(r'\+[-+]+\+', line):
                tables.append(line)

            if current_q_num:
                current_block.append(line)

        if current_q_num and current_block:
            question_blocks.append({
                "question_number": current_q_num,
                "content": "\n".join(current_block)
            })

        return {
            "header": headers,
            "footer": footers,
            "question_blocks": question_blocks,
            "tables": tables,
            "figures": figures,
            "equations": equations,
            "code_blocks": code_blocks,
            "copo_tables": copo_tables,
            "mark_allocations": mark_allocations,
            "page_numbers": page_numbers
        }
