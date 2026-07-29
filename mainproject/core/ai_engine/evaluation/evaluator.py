import time
from typing import Dict, Any, Optional
from core.models import AnswerSegment, Evaluation, AIConfiguration, Rubric
from core.ai_engine.providers.factory import AIProviderFactory
from core.ai_engine.feedback_learning.rag import FeedbackRAGStore
from core.ai_engine.memory.audit import AIMemoryLogger
from .prompt_builder import EvaluationPromptBuilder

class AIEvaluationEngine:
    """
    Core AI Evaluation Engine orchestrating Providers, RAG Exemplars, Scoring, and Audit Logging.
    """

    def __init__(self, config: Optional[AIConfiguration] = None):
        self.config = config or AIConfiguration.get_config()
        self.provider = AIProviderFactory.get_provider(self.config)

    def evaluate_segment(self, segment: AnswerSegment) -> Evaluation:
        """
        Evaluates a single AnswerSegment, calculates marks, records Evaluation, and writes AIMemoryLog.
        """
        start_time = time.time()
        question = segment.question
        rubric = getattr(question, 'rubric', None)
        rubric_text = rubric.criteria if rubric else f"Evaluate for accuracy for Q{question.question_number}."

        # RAG Exemplar Retrieval
        exemplars = []
        if self.config.enable_rag_learning:
            exemplars = FeedbackRAGStore.get_similar_corrections(question, segment.extracted_text)

        # Call AI Provider
        eval_result = self.provider.evaluate_answer(
            question_text=question.prompt_text,
            rubric_criteria=rubric_text,
            student_answer=segment.extracted_text,
            max_marks=float(question.max_marks),
            exemplars=exemplars,
            custom_instructions=self.config.prompt_template
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Create or update Evaluation
        evaluation, _ = Evaluation.objects.get_or_create(segment=segment)
        evaluation.ai_suggested_marks = eval_result.get('ai_suggested_marks', 0.0)
        evaluation.ai_feedback = eval_result.get('ai_feedback', '')
        evaluation.confidence_score = float(eval_result.get('confidence_score', 0.85))
        evaluation.save()

        # Audit Logging
        prompt_snapshot = EvaluationPromptBuilder.build_prompt(question, segment.extracted_text, rubric, exemplars, self.config)
        AIMemoryLogger.log_evaluation(
            evaluation=evaluation,
            provider_name=self.config.provider,
            model_version=getattr(self.provider, 'model_name', 'default'),
            prompt_snapshot=prompt_snapshot,
            raw_response=eval_result,
            confidence_score=evaluation.confidence_score,
            latency_ms=latency_ms
        )

        return evaluation
