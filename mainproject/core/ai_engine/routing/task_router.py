import time
import re
from typing import Dict, Any, List, Optional, Type, Tuple
from core.ai_engine.providers.base import BaseAIProvider
from core.ai_engine.providers.groq import GroqProvider
from core.ai_engine.providers.gemini import GeminiProvider
from core.ai_engine.providers.openai import OpenAIProvider
from core.ai_engine.providers.openrouter import OpenRouterProvider
from core.ai_engine.providers.ollama import OllamaProvider
from core.ai_engine.providers.local_vision import LocalOfflineVisionProvider
from .task_types import TaskType, ProviderStrategy

class ProviderHealthTracker:
    """
    In-process health tracker and cooldown manager for AI Provider classes.
    Prevents repeated calls to dead/rate-limited providers within the cooldown period.
    """

    _cooldowns: Dict[str, float] = {}

    @classmethod
    def mark_cooldown(cls, provider_class_or_name: Any, duration_seconds: float = 60.0):
        name = provider_class_or_name if isinstance(provider_class_or_name, str) else provider_class_or_name.__name__
        cls._cooldowns[name] = time.monotonic() + duration_seconds
        print(f"[PROVIDER COOLDOWN ALERT] {name} placed on cooldown for {duration_seconds:.0f}s.")

    @classmethod
    def is_on_cooldown(cls, provider_class_or_name: Any) -> bool:
        name = provider_class_or_name if isinstance(provider_class_or_name, str) else provider_class_or_name.__name__
        expiry = cls._cooldowns.get(name, 0.0)
        if time.monotonic() < expiry:
            return True
        if name in cls._cooldowns:
            del cls._cooldowns[name]
        return False

    @classmethod
    def clear_cooldowns(cls):
        cls._cooldowns.clear()


class TaskRouter:
    """
    Production Task-Based AI Provider Router for IntelliGrade.
    Enforces Deterministic-First policy, capability-aware routing, image batching,
    non-transient cooldown tracking, and zero score fabrication.
    """

    TASK_CHAINS: Dict[TaskType, List[Type[BaseAIProvider]]] = {
        TaskType.OCR_TEXT: [GeminiProvider, GroqProvider, LocalOfflineVisionProvider, OllamaProvider, OpenAIProvider, OpenRouterProvider],
        TaskType.ROUTINE_PARSE: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
        TaskType.QUESTION_MAPPING: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
        TaskType.ANSWER_VISUAL_READ: [GeminiProvider, GroqProvider, LocalOfflineVisionProvider, OpenAIProvider, OpenRouterProvider],
        TaskType.ANSWER_GRADING: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
        TaskType.FEEDBACK_GENERATION: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
        TaskType.REPORT_SUMMARY: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
        TaskType.COMPLEX_REASONING: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
        TaskType.GENERIC: [GroqProvider, GeminiProvider, OpenAIProvider, OllamaProvider, OpenRouterProvider],
    }

    TASK_MAX_IMAGES: Dict[TaskType, int] = {
        TaskType.OCR_TEXT: 1,
        TaskType.ROUTINE_PARSE: 2,
        TaskType.QUESTION_MAPPING: 0,
        TaskType.ANSWER_VISUAL_READ: 5,
        TaskType.ANSWER_GRADING: 5,
        TaskType.FEEDBACK_GENERATION: 0,
        TaskType.REPORT_SUMMARY: 0,
        TaskType.COMPLEX_REASONING: 5,
        TaskType.GENERIC: 5,
    }

    @classmethod
    def is_transient_error(cls, error_msg: str) -> bool:
        """
        Classifies errors into transient (eligible for single retry) vs non-transient.
        Transient: temporary remote network hiccup, 502 Bad Gateway, 503 Service Unavailable.
        Non-transient: Connection Refused (dead local daemon), 401 Auth, 403 Forbidden, 429 Rate Limit, insufficient_quota.
        """
        if not error_msg or not isinstance(error_msg, str):
            return False
        err_lower = error_msg.lower()

        # Immediate failover for dead local daemons / connection refused
        if any(term in err_lower for term in ['connection refused', 'failed to establish a new connection', '10061', 'winerror 10061', 'refused']):
            return False

        if any(term in err_lower for term in ['401', '403', '429', 'unauthorized', 'invalid api key', 'insufficient_quota', 'quota_exceeded', 'resource_exhausted', 'model_not_found']):
            return False

        if any(term in err_lower for term in ['timed out', 'timeout', '502', '503', 'service unavailable', 'network failure']):
            return True

        return False

    @classmethod
    def route(
        cls,
        task_type: TaskType,
        has_images: bool = False,
        image_count: int = 0,
        required_quality: str = "HIGH",
        budget_mode: str = "BALANCED",
        available_providers: Optional[List[BaseAIProvider]] = None
    ) -> ProviderStrategy:
        preferred_classes = cls.TASK_CHAINS.get(task_type, [GroqProvider, OpenRouterProvider, GeminiProvider, OpenAIProvider])
        requires_local = (task_type == TaskType.QUESTION_MAPPING) or (task_type == TaskType.ROUTINE_PARSE)
        requires_json = task_type in [TaskType.ROUTINE_PARSE, TaskType.QUESTION_MAPPING, TaskType.ANSWER_GRADING, TaskType.REPORT_SUMMARY, TaskType.COMPLEX_REASONING]
        effective_image_count = image_count if image_count > 0 else (1 if has_images else 0)
        has_imgs = has_images or (effective_image_count > 0)
        max_imgs = cls.TASK_MAX_IMAGES.get(task_type, 5 if has_imgs else 0)

        candidate_chain = []
        for p_cls in preferred_classes:
            if ProviderHealthTracker.is_on_cooldown(p_cls):
                print(f"[TASK ROUTER] Skipping {p_cls.__name__} (Active Cooldown)")
                continue

            caps = getattr(p_cls, 'capabilities', {})
            if available_providers:
                matching_instances = [inst for inst in available_providers if isinstance(inst, p_cls)]
                if matching_instances:
                    p_inst = matching_instances[0]
                    caps = p_inst.get_capabilities()

            if has_imgs:
                if not caps.get('supports_images', False):
                    print(f"[TASK ROUTER] Skipping {p_cls.__name__} (Does not support images)")
                    continue
                prov_max_images = caps.get('max_images', 1)
                if effective_image_count > prov_max_images:
                    print(f"[TASK ROUTER] ROUTED WITH COMPACTION: image_count exceeds provider max_images ({effective_image_count} > {prov_max_images}) for {p_cls.__name__}")

            if requires_json and not caps.get('supports_json', False):
                print(f"[TASK ROUTER] Skipping {p_cls.__name__} (Does not support JSON)")
                continue

            candidate_chain.append(p_cls)

        # Set 30.0s timeout budget for local CPU inference on Moondream/Ollama, 6.0s for cloud APIs
        is_local_cpu_inference = any(
            issubclass(p, (LocalOfflineVisionProvider, OllamaProvider)) or p in (LocalOfflineVisionProvider, OllamaProvider)
            for p in candidate_chain
        )
        timeout_budget = 30.0 if is_local_cpu_inference else 6.0

        return ProviderStrategy(
            task_type=task_type,
            execution_chain=candidate_chain,
            requires_local_deterministic=requires_local,
            max_images=max_imgs,
            requires_json=requires_json,
            timeout_seconds=timeout_budget,
            manual_review_threshold=0.70
        )

    @staticmethod
    def batch_images(image_crops: List[Any], max_images: int) -> List[List[Any]]:
        """
        Batches an array of image crops into sub-lists of length <= max_images.
        Ensures 0 images are silently dropped.
        """
        if not image_crops:
            return []
        if max_images <= 0 or len(image_crops) <= max_images:
            return [image_crops]

        batches = []
        for i in range(0, len(image_crops), max_images):
            batches.append(image_crops[i:i + max_images])
        return batches
