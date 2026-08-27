import datetime
from typing import Dict, List, Any, Optional

MODEL_REGISTRY = {
    "gemini": {
        "models": ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"],
        "capabilities": {
            "supports_text": True,
            "supports_images": True,
            "supports_pdf": True,
            "supports_json": True,
            "supports_function_calling": True,
            "max_images": 16
        }
    },
    "openai": {
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        "capabilities": {
            "supports_text": True,
            "supports_images": True,
            "supports_pdf": False,
            "supports_json": True,
            "supports_function_calling": True,
            "max_images": 10
        }
    },
    "groq": {
        "models": ["qwen/qwen3.6-27b", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "capabilities": {
            "supports_text": True,
            "supports_images": True,
            "supports_pdf": False,
            "supports_json": True,
            "supports_function_calling": False,
            "max_images": 3
        }
    },
    "openrouter": {
        "models": ["openrouter/free"],
        "capabilities": {
            "supports_text": True,
            "supports_images": True,
            "supports_pdf": False,
            "supports_json": True,
            "supports_function_calling": False,
            "max_images": 5
        }
    },
    "ollama": {
        "models": ["llama3", "mistral"],
        "capabilities": {
            "supports_text": True,
            "supports_images": False,
            "supports_pdf": False,
            "supports_json": True,
            "supports_function_calling": False,
            "max_images": 0
        }
    }
}

class ModelRegistryManager:
    """
    Centralized Model Registry and Dynamic Failover Manager.
    Tracks model deprecations, rate limits, and selects active models.
    """

    @staticmethod
    def get_models_for_provider(provider_name: str) -> List[str]:
        key = provider_name.lower().replace("provider", "")
        return MODEL_REGISTRY.get(key, {}).get("models", ["AUTO"])

    @staticmethod
    def get_capabilities_for_provider(provider_name: str) -> Dict[str, bool]:
        key = provider_name.lower().replace("provider", "")
        return MODEL_REGISTRY.get(key, {}).get("capabilities", {
            "supports_text": True, "supports_images": False, "supports_pdf": False, "supports_json": True
        })

    @staticmethod
    def get_active_model(provider_name: str) -> str:
        models = ModelRegistryManager.get_models_for_provider(provider_name)
        try:
            from core.models import AIProviderHealth
            health = AIProviderHealth.objects.filter(provider_name__icontains=provider_name).first()
            if health and health.current_model and health.current_model in models:
                if health.status == AIProviderHealth.HealthStatus.HEALTHY:
                    return health.current_model
        except Exception:
            pass
        return models[0] if models else "AUTO"

    @staticmethod
    def validate_active_models():
        """
        Application startup validator verifying configured model availability across providers.
        Ensures deprecated model strings are filtered out and status set to HEALTHY.
        """
        try:
            from core.models import AIProviderHealth
            for provider_key in MODEL_REGISTRY:
                p_name = f"{provider_key.title()}Provider"
                models = MODEL_REGISTRY[provider_key]["models"]
                caps = MODEL_REGISTRY[provider_key]["capabilities"]
                obj, _ = AIProviderHealth.objects.get_or_create(provider_name=p_name)
                if not obj.current_model or obj.current_model not in models:
                    obj.current_model = models[0]
                if obj.status not in [AIProviderHealth.HealthStatus.RATE_LIMITED, AIProviderHealth.HealthStatus.EXPIRED]:
                    obj.status = AIProviderHealth.HealthStatus.HEALTHY
                obj.capabilities_json = caps
                obj.save()
        except Exception as e:
            print(f"[MODEL REGISTRY VALIDATION WARNING] {e}")

    @staticmethod
    def handle_model_error(provider_name: str, failed_model: str, error_msg: str) -> str:
        """
        Marks model as deprecated/rate-limited in DB and selects the next available model.
        """
        models = ModelRegistryManager.get_models_for_provider(provider_name)
        err_lower = str(error_msg).lower()
        
        is_deprecated = "404" in error_msg or "deprecated" in err_lower or "unavailable" in err_lower or "not found" in err_lower
        is_rate_limit = "429" in error_msg or "quota" in err_lower or "resource_exhausted" in err_lower

        next_model = models[0]
        if failed_model in models:
            idx = models.index(failed_model)
            if idx + 1 < len(models):
                next_model = models[idx + 1]

        try:
            from django.utils import timezone
            from core.models import AIProviderHealth
            now = timezone.now()
            obj, _ = AIProviderHealth.objects.get_or_create(provider_name=provider_name)
            obj.current_model = next_model
            obj.capabilities_json = ModelRegistryManager.get_capabilities_for_provider(provider_name)
            
            if is_deprecated:
                obj.status = AIProviderHealth.HealthStatus.EXPIRED
                obj.last_error_message = f"Model '{failed_model}' Deprecated/404: {error_msg[:300]}. Switched to '{next_model}'."
            elif is_rate_limit:
                obj.status = AIProviderHealth.HealthStatus.RATE_LIMITED
                obj.last_error_message = f"Model '{failed_model}' Rate-Limited/429: {error_msg[:300]}. Switched to '{next_model}'."
            else:
                obj.status = AIProviderHealth.HealthStatus.OFFLINE
                obj.last_error_message = str(error_msg)[:500]

            obj.last_failure_at = now
            obj.error_count += 1
            obj.save()
            print(f"[MODEL REGISTRY ALERT] {provider_name} Model '{failed_model}' Error. Auto-switched to '{next_model}'.")
        except Exception as e:
            print(f"[MODEL REGISTRY WARNING] Could not update health log: {e}")

        return next_model
