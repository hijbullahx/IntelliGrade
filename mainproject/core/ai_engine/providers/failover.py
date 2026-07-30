import os
from typing import Dict, Any, Optional, List
from django.conf import settings
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider

class FailoverAIProvider(BaseAIProvider):
    """
    Resilient Multi-Provider Failover Orchestrator for IntelliGrade.
    Chain Sequence: Gemini (Vision/Text) -> Groq (Llama-3 70B) -> OpenAI (GPT-4o) -> Ollama (Local)
    If any provider hits a rate limit (HTTP 429), quota exhaustion, or network timeout,
    the failover chain seamlessly routes to the next active provider without data loss.
    """

    def __init__(self, primary_provider: BaseAIProvider):
        self.primary_provider = primary_provider
        self._chain: List[BaseAIProvider] = []
        self._build_chain()

    def _build_chain(self):
        # 1. Add primary provider
        self._chain.append(self.primary_provider)

        gemini_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
        groq_key = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
        openai_key = getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')

        # 2. Add Groq if not primary
        if groq_key and not isinstance(self.primary_provider, GroqProvider):
            self._chain.append(GroqProvider(api_key=groq_key))

        # 3. Add Gemini if not primary
        if gemini_key and not isinstance(self.primary_provider, GeminiProvider):
            self._chain.append(GeminiProvider(api_key=gemini_key))

        # 4. Add OpenAI if not primary
        if openai_key and not isinstance(self.primary_provider, OpenAIProvider):
            self._chain.append(OpenAIProvider(api_key=openai_key))

        # 5. Add Ollama local fallback
        if not isinstance(self.primary_provider, OllamaProvider):
            self._chain.append(OllamaProvider())

    def _execute_with_failover(self, method_name: str, *args, **kwargs) -> Any:
        last_error = None
        for provider in self._chain:
            try:
                method = getattr(provider, method_name, None)
                if method and callable(method):
                    res = method(*args, **kwargs)
                    if res and not (isinstance(res, str) and "quota_exceeded" in res):
                        return res
            except Exception as e:
                last_error = str(e)
                continue

        raise Exception(f"All AI Providers in the failover chain failed. Last error: {last_error}")

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        return self._execute_with_failover('generate_completion', prompt, system_instruction=system_instruction)

    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        return self._execute_with_failover(
            'evaluate_answer',
            question_text,
            rubric_criteria,
            student_answer,
            max_marks,
            exemplars=exemplars,
            custom_instructions=custom_instructions
        )

    def analyze_question_paper(self, paper_text_or_image: Any, **kwargs) -> Dict[str, Any]:
        return self._execute_with_failover('analyze_question_paper', paper_text_or_image, **kwargs)

    def analyze_academic_exam_paper(self, qp_text_or_bytes: Any, outline_text_or_bytes: Any = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', extra_files: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return self._execute_with_failover('analyze_academic_exam_paper', qp_text_or_bytes, outline_text_or_bytes=outline_text_or_bytes, image_bytes=image_bytes, mime_type=mime_type, extra_files=extra_files)

    def analyze_question_full(self, question_text: str, max_marks: float = 10.0, course_outline_text: str = '') -> Dict[str, Any]:
        return self._execute_with_failover('analyze_question_full', question_text, max_marks=max_marks, course_outline_text=course_outline_text)

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None) -> Dict[str, Any]:
        return self._execute_with_failover('generate_rubric', question_text, max_marks, sample_answer=sample_answer)

    def extract_ocr_text(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        return self._execute_with_failover('extract_ocr_text', image_bytes, mime_type=mime_type)
