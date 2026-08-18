import re
import json
from typing import Dict, Any, List, Optional
from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.retrieval.rag_retriever import RAGRetriever
from core.ai_engine.confidence.confidence_engine import ConfidenceEngine

class AcademicEvaluator:
    """
    Production Academic Script Evaluator for IntelliGrade.
    Evaluates theory, numerical, algorithms, design, code, diagrams, and math derivations
    against Rubrics, Expected Answers, and Historical Teacher Corrections using RAG.
    Returns ONLY Structured JSON.
    """

    def __init__(self):
        self.rag_retriever = RAGRetriever()

    def evaluate(
        self,
        question_id: Optional[int],
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        expected_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        provider = AIProviderFactory.get_provider()

        # Step 1: Retrieve RAG Exemplars (Historical Teacher Corrections)
        exemplars = self.rag_retriever.retrieve_past_corrections(question_id, student_answer, top_k=3)
        exemplar_str = ""
        if exemplars:
            exemplar_str = "Historical Teacher Grading Corrections (Use for Alignment):\n" + "\n".join(
                [f"- Student Answer: {ex['student_answer']}\n  AI Marks: {ex['ai_marks']} -> Teacher Adjusted Marks: {ex['teacher_marks']}\n  Reason: {ex['correction_reason']}" for ex in exemplars]
            )

        prompt = f"""
You are an expert Academic Examiner evaluating a student answer script.

Question: {question_text}
Maximum Marks: {max_marks}
Grading Rubric / Criteria: {rubric_criteria}
Expected Model Answer: {expected_answer or 'Model solution'}

{exemplar_str}

Student Answer Script Text:
{student_answer}

Return ONLY a raw, valid JSON object matching this exact schema:
{{
  "ai_suggested_marks": float,
  "confidence_score": float (0.0 to 1.0),
  "reason": "Detailed grading rationale...",
  "strengths": ["Clear explanation of core concept"],
  "missing_points": ["Missing complexity proof"],
  "incorrect_points": ["Confused worst case with average case"],
  "ai_feedback": "Comprehensive feedback to student...",
  "partial_marking_breakdown": {{"core_concept": 5.0, "examples": 3.0}}
}}
"""
        try:
            raw_res = provider.generate_completion(prompt, system_instruction="Return ONLY raw JSON.")
            cleaned = re.sub(r'```json\s*', '', raw_res)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and 'ai_suggested_marks' in parsed:
                marks = min(max(0.0, float(parsed.get('ai_suggested_marks', 0.0))), float(max_marks))
                parsed['ai_suggested_marks'] = marks
                conf = float(parsed.get('confidence_score') or 0.88)
                parsed['confidence_details'] = ConfidenceEngine.categorize_confidence(conf)
                return parsed
        except Exception:
            pass

        # Fallback structured JSON evaluation when AI provider fails or returns unparseable JSON
        conf_details = ConfidenceEngine.categorize_confidence(0.0)

        return {
            "ai_suggested_marks": 0.0,
            "confidence_score": 0.0,
            "reason": "AI evaluation unavailable or returned unparseable JSON; manual teacher review required.",
            "strengths": [],
            "missing_points": ["AI evaluation unavailable/unparseable."],
            "incorrect_points": [],
            "ai_feedback": "AI evaluation unavailable; manual teacher review required.",
            "partial_marking_breakdown": {},
            "requires_manual_review": True,
            "confidence_details": conf_details
        }
