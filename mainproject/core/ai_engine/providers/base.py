import re
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseAIProvider(ABC):
    """
    Abstract Base Class for all AI LLM Providers in IntelliGrade.
    Enforces SOLID principles (Interface Segregation & Dependency Inversion).
    """

    @abstractmethod
    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates raw text completion from prompt."""
        pass

    @abstractmethod
    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a student's answer segment against rubric criteria and returns structured JSON.
        """
        pass

    @abstractmethod
    def analyze_question_paper(self, paper_text_or_image: Any) -> Dict[str, Any]:
        """
        Analyzes a question paper to extract structured questions, marks, and subquestions.
        """
        pass

    @abstractmethod
    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a suggested grading rubric, key points, and mark distribution for a question.
        """
        pass

    def extract_ocr_text(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Extracts text from document image via multimodal vision."""
        return ""

    def analyze_academic_exam_paper(self, qp_text_or_bytes: Any, outline_text_or_bytes: Any = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', extra_files: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Base implementation for analyzing academic question papers across all providers."""
        doc_text = str(qp_text_or_bytes) if (qp_text_or_bytes and isinstance(qp_text_or_bytes, str)) else 'Academic Examination Paper'
        
        prompt = f"""
You are an expert University Academic Examination Question Scanner and OCR Engine.
Read the examination paper document text carefully and extract ALL examination questions, sub-parts, allocated marks, command verbs, Bloom taxonomy levels, CO/PO mappings, and expected answer criteria.

CRITICAL INSTRUCTION:
1. Extract EVERY SINGLE question (Question 1, Question 2, Question 3, Question 4, etc.) from the entire paper.
2. Escape all backslashes in mathematical formulas or LaTeX equations (e.g. write \\\\begin{{bmatrix}} instead of \\begin{{bmatrix}}).

Question Paper Document Content:
{doc_text}

Return ONLY a valid JSON object in this exact schema without any markdown or commentary:
{{
  "questions": [
    {{
      "question_number": "e.g. Q1",
      "prompt_text": "Exact text of the question statement from the paper",
      "allocated_marks": 25.0,
      "question_type": ["Theory", "Explanation"],
      "command_verbs": ["Explain", "Calculate"],
      "bloom_level": "Apply",
      "co_mapping": "CO2",
      "po_mapping": ["PO1"],
      "criteria": "Key criteria for grading",
      "ideal_answer": "Expected model answer summary"
    }}
  ]
}}
"""
        response_text = self.generate_completion(prompt, system_instruction="Return ONLY raw JSON without commentary.")
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()

        # Direct JSON parse
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                return parsed
        except Exception:
            pass

        # Fix unescaped LaTeX backslashes
        try:
            fixed_escapes = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', cleaned)
            parsed = json.loads(fixed_escapes)
            if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                return parsed
        except Exception:
            pass

        match = re.search(r'(\{[\s\S]*\})', response_text)
        if match:
            try:
                parsed = json.loads(match.group(1))
                if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                    return parsed
            except Exception:
                try:
                    fixed_match = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', match.group(1))
                    parsed = json.loads(fixed_match)
                    if isinstance(parsed, dict) and 'questions' in parsed and parsed['questions']:
                        return parsed
                except Exception:
                    pass

        return {"questions": []}
