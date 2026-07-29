from typing import Dict, Any
from core.models import AIConfiguration

class AIConfigManager:
    """
    Service for reading and updating AI Engine system configuration parameters.
    """

    @staticmethod
    def get_settings() -> AIConfiguration:
        return AIConfiguration.get_config()

    @staticmethod
    def update_settings(
        provider: str = None,
        gemini_model: str = None,
        openai_model: str = None,
        ocr_engine: str = None,
        preprocess: bool = None,
        confidence_threshold: float = None,
        enable_rag: bool = None,
        prompt_template: str = None
    ) -> AIConfiguration:
        
        config = AIConfiguration.get_config()
        if provider:
            config.provider = provider
        if gemini_model:
            config.gemini_model_name = gemini_model
        if openai_model:
            config.openai_model_name = openai_model
        if ocr_engine:
            config.ocr_engine = ocr_engine
        if preprocess is not None:
            config.preprocess_image = preprocess
        if confidence_threshold is not None:
            config.confidence_threshold = confidence_threshold
        if enable_rag is not None:
            config.enable_rag_learning = enable_rag
        if prompt_template is not None:
            config.prompt_template = prompt_template

        config.save()
        return config
