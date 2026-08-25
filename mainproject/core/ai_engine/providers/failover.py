import os
import time
import inspect
from typing import Dict, Any, Optional, List
from django.conf import settings
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider
from .local_vision import LocalOfflineVisionProvider
from core.ai_engine.routing.task_types import TaskType, ProviderStrategy
from core.ai_engine.routing.task_router import TaskRouter, ProviderHealthTracker

class FailoverAIProvider(BaseAIProvider):
    """
    Resilient Multi-Provider Task-Aware Failover Orchestrator for IntelliGrade.
    Integrates TaskRouter, capability matrix matching, transient retry policy,
    non-transient cooldown tracking, global timeout budget enforcement, and OpenRouter support.
    """

    def __init__(self, primary_provider: Optional[BaseAIProvider] = None):
        self.primary_provider = primary_provider
        self._chain: List[BaseAIProvider] = []
        self._build_chain()

    def _build_chain(self):
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
        groq_key = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
        openai_key = getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')
        openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', '') or os.environ.get('OPENROUTER_API_KEY', '')

        self._chain = []
        if self.primary_provider:
            self._chain.append(self.primary_provider)

        if gemini_key and not any(isinstance(p, GeminiProvider) for p in self._chain):
            self._chain.append(GeminiProvider(api_key=gemini_key))

        if groq_key and not any(isinstance(p, GroqProvider) for p in self._chain):
            self._chain.append(GroqProvider(api_key=groq_key))

        if openai_key and not any(isinstance(p, OpenAIProvider) for p in self._chain):
            self._chain.append(OpenAIProvider(api_key=openai_key))

        if openrouter_key and not any(isinstance(p, OpenRouterProvider) for p in self._chain):
            self._chain.append(OpenRouterProvider(api_key=openrouter_key))

        if not any(isinstance(p, LocalOfflineVisionProvider) for p in self._chain):
            self._chain.append(LocalOfflineVisionProvider())

        if not any(isinstance(p, OllamaProvider) for p in self._chain):
            self._chain.append(OllamaProvider())

        print(f"[AI PROVIDER STATUS] Groq: {'CONFIGURED' if groq_key else 'NOT CONFIGURED'} | Gemini: {'CONFIGURED' if gemini_key else 'NOT CONFIGURED'} | OpenAI: {'CONFIGURED' if openai_key else 'NOT CONFIGURED'} | OpenRouter: {'CONFIGURED' if openrouter_key else 'NOT CONFIGURED'} | Local Offline Vision: CONFIGURED | Ollama: CONFIGURED")

    @staticmethod
    def _extract_image_count(args: tuple, kwargs: dict) -> int:
        if 'image_count' in kwargs and isinstance(kwargs['image_count'], int) and kwargs['image_count'] > 0:
            return kwargs['image_count']
        count = 0
        if kwargs.get('image_bytes'):
            count += 1
        elif args:
            for a in args:
                if isinstance(a, (bytes, bytearray)):
                    count += 1
                    break
        extra_files = kwargs.get('extra_files')
        if extra_files and isinstance(extra_files, list):
            count += len(extra_files)
        images = kwargs.get('images')
        if images and isinstance(images, list):
            count += len(images)
        return count

    def _get_execution_chain(self, has_images: bool = False, task_type: Optional[TaskType] = None, image_count: int = 0) -> List[BaseAIProvider]:
        effective_image_count = image_count if image_count > 0 else (1 if has_images else 0)
        has_imgs = has_images or (effective_image_count > 0)
        if task_type:
            strategy = TaskRouter.route(
                task_type=task_type,
                has_images=has_imgs,
                image_count=effective_image_count,
                available_providers=self._chain
            )
            ordered_providers = []
            for p_cls in strategy.execution_chain:
                matching = [p for p in self._chain if isinstance(p, p_cls)]
                if matching:
                    p_inst = matching[0]
                    if not ProviderHealthTracker.is_on_cooldown(p_cls):
                        caps = p_inst.get_capabilities()
                        if has_imgs and not caps.get('supports_images', False):
                            continue
                        ordered_providers.append(p_inst)
            if ordered_providers:
                return ordered_providers

        # Legacy fallback when task_type is None or strategy is unmapped
        if has_imgs:
            order_priority = {
                GeminiProvider: 1,
                OpenAIProvider: 2,
                OpenRouterProvider: 3,
                GroqProvider: 4
            }
            available = [
                p for p in self._chain
                if p.get_capabilities().get('supports_images', False)
                and not ProviderHealthTracker.is_on_cooldown(p.__class__)
            ]
            available.sort(key=lambda p: order_priority.get(p.__class__, 99))
            return available
        else:
            order_priority = {
                GroqProvider: 1,
                OpenRouterProvider: 2,
                GeminiProvider: 3,
                OpenAIProvider: 4,
                OllamaProvider: 5
            }
            available = [p for p in self._chain if p.get_capabilities().get('supports_text', False) and not ProviderHealthTracker.is_on_cooldown(p.__class__)]
            available.sort(key=lambda p: order_priority.get(p.__class__, 99))
            return available

    def _execute_with_failover(self, method_name: str, *args, **kwargs) -> Any:
        passed_timeout = kwargs.get('timeout')
        task_type = kwargs.pop('task_type', None)
        image_count = self._extract_image_count(args, kwargs)
        has_images = bool(image_count > 0 or kwargs.get('image_bytes') or kwargs.get('extra_files') or (args and any(isinstance(a, bytes) for a in args)))

        # Auto-infer task_type if not explicitly provided
        if task_type is None:
            if method_name == 'evaluate_answer':
                task_type = TaskType.ANSWER_VISUAL_READ if has_images else TaskType.ANSWER_GRADING
            elif method_name == 'generate_completion' and has_images:
                task_type = TaskType.ANSWER_VISUAL_READ
            elif method_name == 'extract_ocr_text':
                task_type = TaskType.OCR_TEXT
            elif method_name == 'analyze_question_paper':
                task_type = TaskType.ROUTINE_PARSE
            elif method_name == 'analyze_academic_exam_paper':
                task_type = TaskType.ANSWER_VISUAL_READ if has_images else TaskType.ROUTINE_PARSE
            elif method_name == 'generate_rubric':
                task_type = TaskType.ANSWER_GRADING
            elif method_name == 'analyze_question_full':
                task_type = TaskType.COMPLEX_REASONING

        # Per-task-type budget overrides — vision grading needs adequate window
        _TASK_BUDGETS = {
            'answer_grading': 30.0,
            'answer_visual_read': 30.0,
            'complex_reasoning': 30.0,
            'ocr_text': 16.0,
        }
        env_budget = float(getattr(settings, 'AI_TOTAL_TIMEOUT_BUDGET', None) or os.environ.get('AI_TOTAL_TIMEOUT_BUDGET', 16.0))
        task_key = task_type.value if task_type else None
        total_budget = _TASK_BUDGETS.get(task_key, env_budget)
        overall_start = time.monotonic()
        deadline = overall_start + total_budget

        chain_order = self._get_execution_chain(has_images=has_images, task_type=task_type, image_count=image_count)
        last_error = "No compatible active AI providers available."

        print(f"[AI TIMING] Failover Orchestrator START: method={method_name} | task={task_type.value if task_type else 'GENERIC'} | images={image_count} | budget={total_budget:.1f}s | providers={[p.__class__.__name__ for p in chain_order]}")

        for provider in chain_order:
            provider_name = provider.__class__.__name__

            if ProviderHealthTracker.is_on_cooldown(provider.__class__):
                print(f"[AI TIMING] Skipping {provider_name} (Active Cooldown)")
                continue

            # Hard Enforcement Guard: verify image limit and compact if necessary
            caps = provider.get_capabilities()
            call_kwargs = dict(kwargs)

            if image_count > 0:
                if not caps.get('supports_images', False):
                    print(f"[FAILOVER ENFORCEMENT] SKIPPED: {provider_name} does not support images")
                    continue
                prov_max = caps.get('max_images', 1)
                if image_count > prov_max:
                    try:
                        from core.ai_engine.evaluation.answer_crop_service import AnswerCropService
                        composites = AnswerCropService.compact_crops_into_composites(
                            primary_crop_bytes=call_kwargs.get('image_bytes'),
                            extra_files=call_kwargs.get('extra_files'),
                            max_composites=prov_max,
                            target_width=650
                        )
                        if composites and len(composites) <= prov_max:
                            call_kwargs['image_bytes'] = composites[0]['image_bytes']
                            call_kwargs['extra_files'] = [
                                {'bytes': c['image_bytes'], 'mime_type': 'image/png', 'page_number': c.get('page_number', 1)}
                                for c in composites[1:]
                            ] if len(composites) > 1 else None
                            print(f"[FAILOVER COMPACTION] Compacted {image_count} crops into {len(composites)} composites for {provider_name}")
                        else:
                            print(f"[FAILOVER ENFORCEMENT] SKIPPED: image_count exceeds provider max_images ({image_count} > {prov_max}) for {provider_name}")
                            continue
                    except Exception as e_comp:
                        print(f"[FAILOVER ENFORCEMENT] Compaction failed ({e_comp}). Skipping {provider_name}")
                        continue

            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 1.0:
                print(f"[AI TIMING] Failover budget exhausted ({remaining_budget:.2f}s remaining). Skipping {provider_name} to guarantee response before web gateway timeout.")
                last_error = f"Global AI timeout budget exhausted ({total_budget:.1f}s)"
                break

            if passed_timeout is not None:
                provider_timeout = min(float(passed_timeout), remaining_budget)
            else:
                provider_timeout = min(float(os.environ.get('AI_REQUEST_TIMEOUT', 8.0)), remaining_budget)
            call_kwargs['timeout'] = provider_timeout

            attempt = 0
            max_attempts = 2  # 1 initial call + max 1 retry for transient errors

            while attempt < max_attempts:
                attempt += 1
                start_time = time.monotonic()
                print(f"[AI TIMING] {provider_name} START (attempt={attempt}/{max_attempts}, timeout={provider_timeout:.1f}s, remaining_budget={remaining_budget:.1f}s)")
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

                    is_transient = TaskRouter.is_transient_error(last_error)
                    if is_transient and attempt < max_attempts:
                        print(f"[AI TIMING] {provider_name} Transient Failure ({last_error[:100]}). Retrying attempt {attempt+1}...")
                        time.sleep(0.5)
                        continue

                    # Non-transient or max attempts reached: mark cooldown and failover
                    is_auth_fail = any(term in last_error.lower() for term in ['401', '403', 'invalid api key', 'unauthenticated'])
                    status_code = 'AUTH_FAILURE' if is_auth_fail else ('RATE_LIMITED' if ('429' in last_error or 'quota' in last_error.lower()) else 'OFFLINE')
                    self.log_health_event(provider_name, status_code, error_msg=last_error, response_time_ms=elapsed_ms)

                    ProviderHealthTracker.mark_cooldown(provider.__class__, duration_seconds=60.0)

                    if is_auth_fail:
                        print(f"[AI PROVIDER AUTH FAILURE] {provider_name}: Authentication error ({last_error[:100]}). Immediately failing over...")
                    else:
                        print(f"[AI TIMING] {provider_name} FAILED in {elapsed:.2f}s: {last_error[:100]}. Switching to next provider in chain...")
                    break

        raise Exception(f"All AI Providers in the failover chain failed. Last error: {last_error}")

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> str:
        task_type = kwargs.pop('task_type', None)
        return self._execute_with_failover('generate_completion', prompt, system_instruction=system_instruction, timeout=timeout, task_type=task_type, **kwargs)


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
        task_type = kwargs.pop('task_type', None)
        return self._execute_with_failover(
            'evaluate_answer',
            question_text,
            rubric_criteria,
            student_answer,
            max_marks,
            exemplars=exemplars,
            custom_instructions=custom_instructions,
            timeout=timeout,
            task_type=task_type,
            **kwargs
        )

    def analyze_question_paper(self, paper_text_or_image: Any, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        task_type = kwargs.pop('task_type', None)
        return self._execute_with_failover('analyze_question_paper', paper_text_or_image, timeout=timeout, task_type=task_type, **kwargs)

    def analyze_academic_exam_paper(self, qp_text_or_bytes: Any, outline_text_or_bytes: Any = None, image_bytes: Optional[bytes] = None, mime_type: str = 'image/jpeg', extra_files: Optional[List[Dict[str, Any]]] = None, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        task_type = kwargs.pop('task_type', None)
        try:
            return self._execute_with_failover('analyze_academic_exam_paper', qp_text_or_bytes, outline_text_or_bytes=outline_text_or_bytes, image_bytes=image_bytes, mime_type=mime_type, extra_files=extra_files, timeout=timeout, task_type=task_type, **kwargs)
        except Exception as chain_err:
            print(f"[FAILOVER CHAIN COMPLETE] All AI providers failed ({chain_err}). Executing deterministic regex question extraction fallback...")
            res = BaseAIProvider.extract_deterministic_regex_questions(str(qp_text_or_bytes))
            if not res.get("questions"):
                raise Exception(f"AI Paper Scan Failed and deterministic regex extraction found no questions ({chain_err})")
            return res

    def analyze_question_full(self, question_text: str, max_marks: float = 10.0, course_outline_text: str = '', timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        task_type = kwargs.pop('task_type', None)
        return self._execute_with_failover('analyze_question_full', question_text, max_marks=max_marks, course_outline_text=course_outline_text, timeout=timeout, task_type=task_type, **kwargs)

    def generate_rubric(self, question_text: str, max_marks: float, sample_answer: Optional[str] = None, timeout: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        task_type = kwargs.pop('task_type', None)
        return self._execute_with_failover('generate_rubric', question_text, max_marks, sample_answer=sample_answer, timeout=timeout, task_type=task_type, **kwargs)

    def extract_ocr_text(self, image_bytes: bytes, mime_type: str = "image/jpeg", timeout: Optional[float] = None, **kwargs) -> str:
        task_type = kwargs.pop('task_type', None)
        return self._execute_with_failover('extract_ocr_text', image_bytes, mime_type=mime_type, timeout=timeout, task_type=task_type, **kwargs)
