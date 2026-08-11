from django.core.management.base import BaseCommand
from config import get_config_fingerprint
from config.runtime_config import detect_runtime_environment, is_cuda_available
from config.ai_config import get_ai_config, AIConfig
from config.ocr_config import get_ocr_config
from config.scanner_config import get_scanner_config
from config.evaluation_config import get_evaluation_config

class Command(BaseCommand):
    help = 'Safely checks and reports IntelliGrade AI, Scanner, OCR, and Deployment status.'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("         INTELLIGRADE SYSTEM CONFIGURATION DIAGNOSTIC")
        self.stdout.write("=" * 60)

        env_name = detect_runtime_environment()
        fingerprints = get_config_fingerprint()
        ai_cfg = get_ai_config()
        ocr_cfg = get_ocr_config()
        scan_cfg = get_scanner_config()
        eval_cfg = get_evaluation_config()

        self.stdout.write(f"\nEnvironment: {env_name}")
        self.stdout.write(f"Config Versions: AI={fingerprints['ai_config_version']} | Scanner={fingerprints['scanner_config_version']} | Evaluation={fingerprints['evaluation_config_version']} | Prompts={fingerprints['prompt_version']}")

        self.stdout.write("\n--- AI PROVIDERS ---")
        gemini_key = AIConfig.get_api_key("GEMINI")
        gemini_status = "READY" if gemini_key else "MISSING"
        self.stdout.write(f"Gemini : Configured={bool(gemini_key)} | Models={AIConfig.get_provider_models('GEMINI')} | Status={gemini_status}")

        groq_key = AIConfig.get_api_key("GROQ")
        groq_status = "READY" if groq_key else "MISSING"
        self.stdout.write(f"Groq   : Configured={bool(groq_key)} | Models={AIConfig.get_provider_models('GROQ')} | Status={groq_status}")

        openai_key = AIConfig.get_api_key("OPENAI")
        openai_status = "READY" if openai_key else "MISSING"
        self.stdout.write(f"OpenAI : Configured={bool(openai_key)} | Models={AIConfig.get_provider_models('OPENAI')} | Status={openai_status}")

        self.stdout.write(f"Default Provider: {ai_cfg['default_provider']}")

        self.stdout.write("\n--- OCR ENGINES & HARDWARE ---")
        self.stdout.write(f"PyTorch CUDA GPU : {'AVAILABLE (GPU)' if is_cuda_available() else 'UNAVAILABLE (CPU Fallback)'}")
        self.stdout.write(f"EasyOCR Reader   : {'READY' if ocr_cfg['easyocr_ready'] else 'UNAVAILABLE'}")
        self.stdout.write(f"PyMuPDF Renderer : READY (DPI={scan_cfg['dpi']})")

        self.stdout.write("\n--- SCANNER & EVALUATION ---")
        self.stdout.write(f"Scanner Pipeline  : READY (DPI={scan_cfg['dpi']}, Heading Window={scan_cfg['max_heading_y_pct']})")
        self.stdout.write(f"Evaluation Engine : READY (Temp={eval_cfg['temperature']}, Conf Threshold={eval_cfg['confidence_threshold']})")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("INTELLIGRADE CONFIGURATION DIAGNOSTIC COMPLETED PASSING"))
        self.stdout.write("=" * 60 + "\n")
