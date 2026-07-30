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
        Evaluates a student's answer segment against rubric criteria and returns structured JSON:
        {
          "ai_suggested_marks": float,
          "confidence_score": float,
          "ai_feedback": str,
          "partial_marking_breakdown": dict
        }
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
