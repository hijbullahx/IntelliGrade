"""
IntelliGrade Global Configuration System v3.0
=============================================
Centralized architecture for environment variables, AI providers, OCR engines,
document scanner parameters, evaluation prompts, and deployment path resolution.
"""

AI_CONFIG_VERSION = "3.0"
SCANNER_CONFIG_VERSION = "3.0"
EVALUATION_CONFIG_VERSION = "3.0"
PROMPT_VERSION = "3.0"

def get_config_fingerprint() -> dict:
    """Returns non-secret version fingerprints across subsystem configs."""
    return {
        "ai_config_version": AI_CONFIG_VERSION,
        "scanner_config_version": SCANNER_CONFIG_VERSION,
        "evaluation_config_version": EVALUATION_CONFIG_VERSION,
        "prompt_version": PROMPT_VERSION,
    }
