import os
from typing import Dict, Any, List
from django.conf import settings
from .runtime_config import load_environment_variables

load_environment_variables()

class AIConfig:
    """Centralized AI Engine Configuration."""

    DEFAULT_MODELS = {
        "GEMINI": ["gemini-2.0-flash", "gemini-2.0-flash-lite"],
        "GROQ": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "OPENAI": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        "OLLAMA": ["llama3", "mistral"],
    }

    FAILOVER_SEQUENCE = ["GEMINI", "GROQ", "OPENAI", "OLLAMA", "MOCK"]

    @classmethod
    def get_api_key(cls, provider: str) -> str:
        provider_upper = provider.upper().replace("PROVIDER", "")
        setting_key = f"{provider_upper}_API_KEY"
        return getattr(settings, setting_key, '') or os.environ.get(setting_key, '')

    @classmethod
    def get_default_provider(cls) -> str:
        return getattr(settings, 'DEFAULT_AI_PROVIDER', '') or os.environ.get('DEFAULT_AI_PROVIDER', 'GROQ')

    @classmethod
    def get_provider_models(cls, provider: str) -> List[str]:
        provider_upper = provider.upper().replace("PROVIDER", "")
        return cls.DEFAULT_MODELS.get(provider_upper, ["AUTO"])

    @classmethod
    def get_timeout_seconds(cls) -> int:
        return int(os.environ.get('AI_REQUEST_TIMEOUT', '60'))

    @classmethod
    def get_max_retries(cls) -> int:
        return int(os.environ.get('AI_MAX_RETRIES', '3'))

def get_ai_config() -> Dict[str, Any]:
    return {
        "default_provider": AIConfig.get_default_provider(),
        "gemini_configured": bool(AIConfig.get_api_key("GEMINI")),
        "groq_configured": bool(AIConfig.get_api_key("GROQ")),
        "openai_configured": bool(AIConfig.get_api_key("OPENAI")),
        "timeout": AIConfig.get_timeout_seconds(),
        "max_retries": AIConfig.get_max_retries(),
    }
