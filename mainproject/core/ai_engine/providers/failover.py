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

        print(f"[AI PROVIDER STATUS] Groq: {'CONFIGURED' if groq_key else 'NOT CONFIGURED'} | Gemini: {'CONFIGURED' if gemini_key else 'NOT CONFIGURED'} | OpenAI: {'CONFIGURED' if openai_key else 'NOT CONFIGURED'} | Ollama: CONFIGURED")

    def _execute_with_failover(self, method_name: str, *args, **kwargs) -> Any:
        import time
        import inspect
        last_error = None
        has_images = bool(kwargs.get('image_bytes') or (args and isinstance(args[0], bytes)))

        total_budget = float(getattr(settings, 'AI_TOTAL_TIMEOUT_BUDGET', None) or os.environ.get('AI_TOTAL_TIMEOUT_BUDGET', 16.0))
        overall_start = time.monotonic()
        deadline = overall_start + total_budget

        # Dynamic Capability-Based Provider Selection
        chain_order = list(self._chain)
        if has_images:
            # Sort vision-capable providers to the front of the chain
            chain_order.sort(key=lambda p: 0 if p.get_capabilities().get('supports_images') else 1)

        print(f"[AI TIMING] Failover Orchestrator START: method={method_name} | budget={total_budget:.1f}s | providers={[p.__class__.__name__ for p in chain_order]}")

        for provider in chain_order:
            provider_name = provider.__class__.__name__
            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 1.0:
                print(f"[AI TIMING] Failover budget exhausted ({remaining_budget:.2f}s remaining). Skipping {provider_name} to guarantee response before web gateway timeout.")
                last_error = f"Global AI timeout budget exhausted ({total_budget:.1f}s)"
                break

            provider_timeout = min(float(os.environ.get('AI_REQUEST_TIMEOUT', 6.0)), remaining_budget)
            call_kwargs = dict(kwargs)
            call_kwargs['timeout'] = provider_timeout

            start_time = time.monotonic()
            print(f"[AI TIMING] {provider_name} START (timeout={provider_timeout:.1f}s, remaining_budget={remaining_budget:.1f}s)")
            try:
                method = getattr(provider, method_name, None)
                if method and callable(method):
                    sig = inspect.signature(method)
                    if 'timeout' in sig.parameters:
                        res = method(*args, **call_kwargs)
                    else:
                        res = method(*args, **kwargs)

                    elapsed = time.monotonic() - start_time
                    if res and not (isinstance(res, str) and "quota_exceeded" in res):
                        elapsed_ms = int(elapsed * 1000)
                        self.log_health_event(provider_name, 'HEALTHY', error_msg="", response_time_ms=elapsed_ms)
                        print(f"[AI TIMING] {provider_name} SUCCESS in {elapsed:.2f}s (Total failover time: {time.monotonic() - overall_start:.2f}s)")
                        return res
            except Exception as e:
                elapsed = time.monotonic() - start_time
                last_error = str(e)
                elapsed_ms = int(elapsed * 1000)
                is_auth_fail = ('401' in last_error or '403' in last_error or 'invalid api key' in last_error.lower() or 'unauthenticated' in last_error.lower() or 'invalid authentication' in last_error.lower())
                status_code = 'AUTH_FAILURE' if is_auth_fail else ('RATE_LIMITED' if ('429' in last_error or 'quota' in last_error.lower()) else 'OFFLINE')
                self.log_health_event(provider_name, status_code, error_msg=last_error, response_time_ms=elapsed_ms)
                if is_auth_fail:
                    print(f"[AI PROVIDER AUTH FAILURE] {provider_name}: Authentication error ({last_error[:100]}). Immediately failing over...")
                else:
                    print(f"[AI TIMING] {provider_name} FAILED in {elapsed:.2f}s: {last_error}. Switching to next provider in chain...")
                continue

        raise Exception(f"All AI Providers in the failover chain failed. Last error: {last_error}")

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> str:
        return self._execute_with_failover('generate_completion', prompt, system_instruction=system_instruction, timeout=timeout, **kwargs)

    def evaluate_answer(
        self,
        question_text: str,
        rubric_criteria: str,
        student_answer: str,
        max_marks: float,
        exemplars: Optional[List[Dict[str, Any]]] = None,
        custom_instructions: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        return self._execute_with_failover(
            'evaluate_answer',
            question_text,
            rubric_criteria,
            student_answer,
            max_marks,
            exemplars=exemplars,
            custom_instructions=custom_instructions,
            timeout=timeout,
            **kwargs
        )

    def analyze_question_paper(self, paper_text_or_image: Any, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        return self._execute_with_failover('analyze_question_paper', paper_text_or_image, timeout=timeout, **kwargs)

    def analyze_academic_exam_paper(self, qp_text_or_bytes: Any, outline_text_or_bytes: Any = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', extra_files: Optional[List[Dict[str, Any]]] = None, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        try:
            return self._execute_with_failover('analyze_academic_exam_paper', qp_text_or_bytes, outline_text_or_bytes=outline_text_or_bytes, image_bytes=image_bytes, mime_type=mime_type, extra_files=extra_files, timeout=timeout, **kwargs)
        except Exception as chain_err:
            print(f"[FAILOVER CHAIN COMPLETE] All AI providers failed ({chain_err}). Executing deterministic regex question extraction fallback...")
            res = BaseAIProvider.extract_deterministic_regex_questions(str(qp_text_or_bytes))
            if not res.get("questions"):
                raise Exception(f"AI Paper Scan Failed and deterministic regex extraction found no questions ({chain_err})")
            return res

    def analyze_question_full(self, question_text: str, max_marks: float = 10.0, course_outline_text: str = '', timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        return self._execute_with_failover('analyze_question_full', question_text, max_marks=max_marks, course_outline_text=course_outline_text, timeout=timeout, **kwargs)

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        return self._execute_with_failover('generate_rubric', question_text, max_marks, sample_answer=sample_answer, timeout=timeout, **kwargs)

    def extract_ocr_text(self, image_bytes: bytes, mime_type: str = "image/jpeg", timeout: Optional[float] = None, **kwargs) -> str:
        return self._execute_with_failover('extract_ocr_text', image_bytes, mime_type=mime_type, timeout=timeout, **kwargs)


