from typing import Dict, Any, Optional
from core.models import AIMemoryLog, Evaluation

class AIMemoryLogger:
    """
    Audit Logger recording LLM execution history, prompt snapshots, response payloads, and performance latency.
    """

    @staticmethod
    def log_evaluation(
        evaluation: Optional[Evaluation],
        provider_name: str,
        model_version: str,
        prompt_snapshot: str,
        raw_response: Dict[str, Any],
        confidence_score: float = 0.0,
        latency_ms: int = 0
    ) -> AIMemoryLog:
        """
        Creates an immutable audit log entry in AIMemoryLog database.
        """
        return AIMemoryLog.objects.create(
            evaluation=evaluation,
            provider=provider_name,
            model_version=model_version,
            prompt_snapshot=prompt_snapshot,
            raw_response_json=raw_response,
            confidence_score=confidence_score,
            latency_ms=latency_ms
        )
