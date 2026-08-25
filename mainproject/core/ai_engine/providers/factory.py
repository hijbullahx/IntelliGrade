import os
from django.conf import settings
from core.models import AIConfiguration
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider
from .mock import MockProvider

from .failover import FailoverAIProvider

class AIProviderFactory:
    """
    Factory Pattern for instantiating AI Providers wrapped in FailoverAIProvider chain.
    """

    @staticmethod
    def get_provider(config: AIConfiguration = None) -> BaseAIProvider:
        default_env_provider = getattr(settings, 'DEFAULT_AI_PROVIDER', '').upper()
        
        groq_key = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
        openai_key = getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')

        primary = None
        if default_env_provider == 'GROQ' and groq_key:
            primary = GroqProvider(api_key=groq_key)
        elif default_env_provider == 'GEMINI' and gemini_key:
            primary = GeminiProvider(api_key=gemini_key)
        elif default_env_provider == 'OPENAI' and openai_key:
            primary = OpenAIProvider(api_key=openai_key)

        if primary is None:
            if config is None:
                config = AIConfiguration.get_config()
            provider_type = config.provider.upper()

            if provider_type == AIConfiguration.Provider.GROQ and groq_key:
                primary = GroqProvider(api_key=groq_key)
            elif provider_type == AIConfiguration.Provider.GEMINI and gemini_key:
                primary = GeminiProvider(api_key=gemini_key, model_name=config.gemini_model_name or 'gemini-flash-latest')
            elif provider_type == AIConfiguration.Provider.OPENAI and openai_key:
                primary = OpenAIProvider(api_key=openai_key, model_name=config.openai_model_name or 'gpt-4o-mini')

        if primary is None:
            if gemini_key:
                primary = GeminiProvider(api_key=gemini_key, model_name='gemini-flash-latest')
            elif groq_key:
                primary = GroqProvider(api_key=groq_key)
            elif openai_key:
                primary = OpenAIProvider(api_key=openai_key)
            else:
                primary = MockProvider()

        return FailoverAIProvider(primary_provider=primary)
