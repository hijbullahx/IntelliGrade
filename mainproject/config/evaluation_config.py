from typing import Dict, Any

class EvaluationConfig:
    TEMPERATURE = 0.2
    MAX_TOKENS = 2048
    TIMEOUT_SECONDS = 60
    MAX_RETRIES = 3
    CONFIDENCE_THRESHOLD = 0.75
    MANUAL_REVIEW_THRESHOLD = 0.70
    ENABLE_RAG_LEARNING = True

def get_evaluation_config() -> Dict[str, Any]:
    return {
        "temperature": EvaluationConfig.TEMPERATURE,
        "max_tokens": EvaluationConfig.MAX_TOKENS,
        "timeout_seconds": EvaluationConfig.TIMEOUT_SECONDS,
        "confidence_threshold": EvaluationConfig.CONFIDENCE_THRESHOLD,
        "manual_review_threshold": EvaluationConfig.MANUAL_REVIEW_THRESHOLD,
        "enable_rag_learning": EvaluationConfig.ENABLE_RAG_LEARNING,
    }
