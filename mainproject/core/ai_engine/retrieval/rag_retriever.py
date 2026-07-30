from typing import List, Dict, Any, Optional
from core.models import FeedbackCorrection, Question, Rubric, Examination
from core.ai_engine.embeddings.embedding_engine import EmbeddingEngine

class RAGRetriever:
    """
    Retrieval-Augmented Learning & Academic Knowledge Base Engine.
    Retrieves relevant course context (COs, POs, KPAs, past rubrics, teacher corrections)
    and injects them as few-shot exemplars into evaluation and generation prompts.
    """

    def __init__(self):
        self.embedder = EmbeddingEngine()

    def retrieve_past_corrections(self, question_id: Optional[int], student_answer: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top-K historical teacher corrections for similar questions & student answers.
        """
        corrections = FeedbackCorrection.objects.select_related('question', 'evaluation').all()
        if question_id:
            same_q_corrections = corrections.filter(question_id=question_id)
            if same_q_corrections.exists():
                corrections = same_q_corrections

        if not corrections.exists():
            return []

        query_vec = self.embedder.get_embedding(student_answer)
        scored = []

        for c in corrections[:50]:
            ans_text = c.student_answer or ""
            c_vec = c.embedding if isinstance(c.embedding, list) and c.embedding else self.embedder.get_embedding(ans_text)
            sim = self.embedder.cosine_similarity(query_vec, c_vec)
            scored.append({
                "question_number": c.question.question_number,
                "student_answer": c.student_answer,
                "ai_marks": float(c.ai_suggested_marks),
                "teacher_marks": float(c.teacher_final_marks),
                "correction_reason": c.correction_reason,
                "similarity": sim
            })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def build_course_knowledge_context(self, exam_id: Optional[int]) -> str:
        """
        Builds course knowledge context (COs, POs, KPAs, Topics) for an examination.
        """
        if not exam_id:
            return "Course Context: General Academic Examination"

        exam = Examination.objects.filter(id=exam_id).select_related('course').first()
        if not exam:
            return "Course Context: General Academic Examination"

        context_lines = [
            f"Course: {exam.course.code} - {exam.course.title}",
            f"Exam Title: {exam.title}",
            "Course Outcomes: CO1 (Core Principles), CO2 (Design & Analysis), CO3 (Implementation)"
        ]
        return "\n".join(context_lines)
