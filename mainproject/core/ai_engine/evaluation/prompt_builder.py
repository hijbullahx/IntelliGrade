from typing import Optional, List, Dict, Any
from core.models import Question, Rubric, AIConfiguration

class EvaluationPromptBuilder:
    """
    Prompt Builder constructing rich zero-shot and RAG few-shot prompts for evaluation.
    """

    @staticmethod
    def build_prompt(
        question: Question,
        student_answer: str,
        rubric: Optional[Rubric] = None,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        config: Optional[AIConfiguration] = None
    ) -> str:
        
        criteria = rubric.criteria if rubric else f"Grade based on correctness for Q{question.question_number}."
        custom_instructions = config.prompt_template if (config and config.prompt_template) else ""

        exemplar_section = ""
        if exemplars:
            exemplar_section = "\n\nPast Teacher Corrections & Exemplars:\n"
            for ex in exemplars:
                exemplar_section += f"- Q: {ex.get('question')}\n  Answer: {ex.get('student_answer')}\n  AI Marks: {ex.get('ai_marks')} -> Teacher Marks: {ex.get('teacher_marks')}\n  Teacher Reason: {ex.get('reason')}\n"

        prompt = f"""
Evaluate the following student answer.

Question #{question.question_number}: {question.prompt_text}
Max Marks: {question.max_marks}

Grading Criteria / Rubric:
{criteria}
{exemplar_section}
{custom_instructions}

Student Answer:
{student_answer}
"""
        return prompt
