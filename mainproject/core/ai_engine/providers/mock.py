from typing import Dict, Any, Optional, List
from .base import BaseAIProvider

class MockProvider(BaseAIProvider):
    """
    Mock AI Provider Implementation for offline testing, local demo, and zero-credential environments.
    """

    capabilities = {
        "supports_text": True,
        "supports_images": True,
        "supports_pdf": False,
        "supports_json": True,
        "supports_function_calling": False,
        "max_images": 10
    }

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        return "Mock Completion Response for testing."

    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        max_m = float(max_marks)
        suggested = round(max_m * 0.85, 2)
        return {
            "ai_suggested_marks": suggested,
            "confidence_score": 0.92,
            "ai_feedback": f"Mock AI Evaluation: Student demonstrated strong understanding of '{question_text[:30]}...'. Awarded {suggested}/{max_m} marks.",
            "partial_marking_breakdown": {
                "key_concepts_identified": round(max_m * 0.5, 2),
                "technical_clarity": round(max_m * 0.35, 2)
            }
        }

    def analyze_question_paper(self, paper_text_or_image: Any) -> Dict[str, Any]:
        return {
            "routine_schedule": [
                {
                    "course_code": "CSE 411",
                    "course_title": "Software Engineering",
                    "faculty_name": "Dr. Alan Turing",
                    "exam_date": "2026-08-15",
                    "exam_time": "10:00 AM - 01:00 PM",
                    "total_marks": 100.0
                },
                {
                    "course_code": "CSE 312",
                    "course_title": "Database Management Systems",
                    "faculty_name": "Prof. Grace Hopper",
                    "exam_date": "2026-08-18",
                    "exam_time": "02:00 PM - 05:00 PM",
                    "total_marks": 100.0
                }
            ]
        }

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None) -> Dict[str, Any]:
        max_m = float(max_marks)
        return {
            "criteria": f"1. Explanation of core concept ({round(max_m*0.4, 2)} marks)\n2. Comparison & key advantages ({round(max_m*0.4, 2)} marks)\n3. Technical diagram or structure ({round(max_m*0.2, 2)} marks)",
            "ideal_answer": f"Ideal answer covering essential architectural principles for question: {question_text}",
            "mark_distribution": {
                "core_explanation": round(max_m * 0.4, 2),
                "advantages_contrast": round(max_m * 0.4, 2),
                "diagram_structure": round(max_m * 0.2, 2)
            }
        }
