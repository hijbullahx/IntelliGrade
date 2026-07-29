import math
from typing import List, Dict, Any
from core.models import FeedbackCorrection, Question, Evaluation

class FeedbackRAGStore:
    """
    RAG Learning Store recording teacher corrections and retrieving relevant exemplars for prompt augmentation.
    """

    @staticmethod
    def _text_to_vector(text: str) -> List[float]:
        """Simple deterministic term frequency vector generator for similarity scoring."""
        words = set(text.lower().split())
        return [float(hash(w) % 100) / 100.0 for w in words] if words else [0.0]

    @classmethod
    def record_correction(
        cls,
        evaluation: Evaluation,
        teacher_marks: float,
        reason: str = ""
    ) -> FeedbackCorrection:
        """
        Records teacher mark modification into FeedbackCorrection store for future AI prompt learning.
        """
        question = evaluation.segment.question
        student_ans = evaluation.segment.extracted_text
        ai_marks = float(evaluation.ai_suggested_marks or 0.0)

        correction, created = FeedbackCorrection.objects.get_or_create(
            evaluation=evaluation,
            defaults={
                'question': question,
                'student_answer': student_ans,
                'ai_suggested_marks': ai_marks,
                'teacher_final_marks': teacher_marks,
                'correction_reason': reason,
                'embedding': cls._text_to_vector(student_ans)
            }
        )
        if not created:
            correction.teacher_final_marks = teacher_marks
            correction.correction_reason = reason
            correction.save()

        return correction

    @classmethod
    def get_similar_corrections(cls, question: Question, student_answer: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top-N past teacher corrections for similar questions/answers to pass as few-shot exemplars to the LLM.
        """
        corrections = FeedbackCorrection.objects.filter(question=question)[:limit]
        exemplars = []
        for c in corrections:
            exemplars.append({
                'question': question.prompt_text,
                'student_answer': c.student_answer,
                'ai_marks': float(c.ai_suggested_marks),
                'teacher_marks': float(c.teacher_final_marks),
                'reason': c.correction_reason or "Teacher adjusted score based on rubric clarity."
            })
        return exemplars
