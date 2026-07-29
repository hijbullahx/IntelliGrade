import os
from django.conf import settings
from core.models import AIConfiguration
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .mock import MockProvider

class AIProviderFactory:
    """
    Factory Pattern for instantiating AI Providers based on AIConfiguration settings.
    """

    @staticmethod
    def get_provider(config: AIConfiguration = None) -> BaseAIProvider:
        if config is None:
            config = AIConfiguration.get_config()

        provider_type = config.provider.upper()

        if provider_type == AIConfiguration.Provider.GEMINI:
            api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
            model_name = config.gemini_model_name or 'gemini-flash-latest'
            if not api_key:
                # Fallback gracefully to Mock if API Key is not set
                return MockProvider()
            return GeminiProvider(api_key=api_key, model_name=model_name)

        elif provider_type == AIConfiguration.Provider.OPENAI:
            api_key = getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')
            model_name = config.openai_model_name or 'gpt-4o-mini'
            if not api_key:
                return MockProvider()
            return OpenAIProvider(api_key=api_key, model_name=model_name)

        else:
            return MockProvider()
