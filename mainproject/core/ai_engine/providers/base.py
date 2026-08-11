import re
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseAIProvider(ABC):
    """
    Abstract Base Class for all AI LLM Providers in IntelliGrade.
    Enforces SOLID principles (Interface Segregation & Dependency Inversion).
    """

    capabilities = {
        "supports_text": True,
        "supports_images": True,
        "supports_pdf": True,
        "supports_json": True,
        "supports_function_calling": False,
        "supports_streaming": False
    }

    def get_capabilities(self) -> Dict[str, bool]:
        """Returns declared capability matrix for provider routing."""
        return getattr(self, 'capabilities', {
            "supports_text": True, "supports_images": False, "supports_pdf": False, "supports_json": True
        })

    @staticmethod
    def log_health_event(provider_name: str, status: str, model_name: str = "AUTO", error_msg: str = "", response_time_ms: int = 0):
        """Logs provider health metrics, status changes, and rate limits to DB."""
        try:
            from django.utils import timezone
            from core.models import AIProviderHealth
            now = timezone.now()
            obj, _ = AIProviderHealth.objects.get_or_create(provider_name=provider_name)
            obj.current_model = model_name
            obj.status = status
            if status == AIProviderHealth.HealthStatus.HEALTHY:
                obj.last_success_at = now
                if response_time_ms > 0:
                    obj.avg_response_time_ms = int((obj.avg_response_time_ms + response_time_ms) / 2) if obj.avg_response_time_ms else response_time_ms
            else:
                obj.last_failure_at = now
                obj.error_count += 1
                obj.last_error_message = str(error_msg)[:500]
            obj.save()
        except Exception:
            pass

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

        # Deterministic Regex Question Fallback Extractor if LLM output fails
        fallback_questions = []
        q_blocks = re.split(r'(?i)(?=(?:question\s*\d+|q\d+[\.\:]?|\b\d+[\.\)]\s+[A-Z]))', doc_text)
        for q_idx, block in enumerate(q_blocks):
            b_text = block.strip()
            if len(b_text) > 20:
                num_match = re.search(r'(?i)(question\s*\d+|q\d+|\b\d+[\.\)])', b_text)
                q_num = num_match.group(1).upper() if num_match else f"Q{q_idx+1}"
                
                # Extract marks if present
                marks_match = re.search(r'\[(\d+(?:\.\d+)?)\s*marks?\]', b_text, re.IGNORECASE)
                allocated_marks = float(marks_match.group(1)) if marks_match else 25.0

                fallback_questions.append({
                    "question_number": q_num,
                    "prompt_text": b_text[:500],
                    "allocated_marks": allocated_marks,
                    "question_type": ["Theory"],
                    "command_verbs": ["Explain"],
                    "bloom_level": "Understand",
                    "co_mapping": "CO1",
                    "po_mapping": ["PO1"],
                    "criteria": "Accurate response covering key concepts.",
                    "ideal_answer": "Model answer covering core concepts."
                })

        return {"questions": fallback_questions if fallback_questions else [
            {
                "question_number": "Q1",
                "prompt_text": doc_text[:500] if doc_text else "Examination Question 1",
                "allocated_marks": 25.0,
                "question_type": ["Theory"],
                "command_verbs": ["Explain"],
                "bloom_level": "Understand",
                "co_mapping": "CO1",
                "po_mapping": ["PO1"],
                "criteria": "Key grading criteria",
                "ideal_answer": "Model answer summary"
            }
        ]}
