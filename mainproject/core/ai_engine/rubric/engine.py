from typing import Dict, Any, Optional
from core.ai_engine.providers.factory import AIProviderFactory
from core.models import Question, Rubric, AIConfiguration

class RubricEngine:
    """
    Engine for generating suggested marking rubrics, mark distributions, and ideal answers.
    """

    def __init__(self, provider=None):
        self.provider = provider or AIProviderFactory.get_provider()

    def generate_and_save_rubric(self, question: Question, sample_answer: Optional[str] = None) -> Rubric:
        """
        Generates suggested rubric using active AI Provider and saves to database.
        """
        data = self.provider.generate_rubric(
            question_text=question.prompt_text,
            max_marks=float(question.max_marks),
            sample_answer=sample_answer
        )

        rubric, created = Rubric.objects.get_or_create(question=question)
        rubric.criteria = data.get('criteria', f'Grading criteria for Q{question.question_number}')
        rubric.ideal_answer = data.get('ideal_answer', sample_answer or '')
        rubric.mark_distribution = data.get('mark_distribution', {})
        rubric.save()
        return rubric
