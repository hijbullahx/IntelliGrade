import os
import sys
import platform
import django
from django.core.management.base import BaseCommand
from django.conf import settings
from config.runtime_config import detect_runtime_environment, is_cuda_available
from config.ai_config import get_ai_config, AIConfig

class Command(BaseCommand):
    help = 'Safely reports complete runtime environment, third-party library versions, database engine, and configuration flags.'

    def handle(self, *args, **options):
        self.stdout.write("=" * 65)
        self.stdout.write("          INTELLIGRADE GLOBAL RUNTIME DIAGNOSTIC")
        self.stdout.write("=" * 65)

        self.stdout.write(f"\n[SYSTEM & PLATFORM]")
        self.stdout.write(f"Python Version    : {sys.version.split()[0]} ({platform.python_implementation()})")
        self.stdout.write(f"Django Version    : {django.get_version()}")
        self.stdout.write(f"OS / Architecture : {platform.system()} {platform.release()} ({platform.machine()})")
        self.stdout.write(f"Runtime Env       : {detect_runtime_environment()}")

        self.stdout.write(f"\n[DATABASE & TIMEZONE]")
        db_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]
        self.stdout.write(f"Database Engine   : {db_engine}")
        self.stdout.write(f"Time Zone         : {settings.TIME_ZONE} (USE_TZ={settings.USE_TZ})")
        self.stdout.write(f"Language Code     : {settings.LANGUAGE_CODE}")

        self.stdout.write(f"\n[THIRD-PARTY LIBRARIES]")
        for pkg, imp_name in [
            ("PyMuPDF", "fitz"),
            ("OpenCV", "cv2"),
            ("Pillow", "PIL"),
            ("EasyOCR", "easyocr"),
            ("PyTorch", "torch"),
            ("NumPy", "numpy"),
            ("Google GenAI", "google.generativeai"),
            ("Groq SDK", "groq"),
            ("OpenAI SDK", "openai"),
        ]:
            try:
                mod = __import__(imp_name, fromlist=['__version__'])
                ver = getattr(mod, '__version__', 'Installed')
                self.stdout.write(f"{pkg:<18} : INSTALLED ({ver})")
            except ImportError:
                self.stdout.write(f"{pkg:<18} : NOT INSTALLED")

        self.stdout.write(f"\n[HARDWARE ACCELERATION]")
        self.stdout.write(f"PyTorch CUDA GPU  : {'AVAILABLE (GPU)' if is_cuda_available() else 'UNAVAILABLE (CPU Fallback)'}")

        self.stdout.write(f"\n[AI PROVIDER & MODELS]")
        ai_info = get_ai_config()
        self.stdout.write(f"Default Provider  : {ai_info['default_provider']}")
        self.stdout.write(f"Gemini API        : {'CONFIGURED' if ai_info['gemini_configured'] else 'MISSING'} | Models={AIConfig.get_provider_models('GEMINI')}")
        self.stdout.write(f"Groq API          : {'CONFIGURED' if ai_info['groq_configured'] else 'MISSING'} | Models={AIConfig.get_provider_models('GROQ')}")
        self.stdout.write(f"OpenAI API        : {'CONFIGURED' if ai_info['openai_configured'] else 'MISSING'} | Models={AIConfig.get_provider_models('OPENAI')}")

        self.stdout.write(f"\n[SECURITY & DEPLOYMENT]")
        self.stdout.write(f"ALLOWED_HOSTS     : {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])}")
        self.stdout.write(f"MEDIA_ROOT        : {settings.MEDIA_ROOT}")
        self.stdout.write(f"STATIC_ROOT       : {settings.STATIC_ROOT}")

        self.stdout.write("\n" + "=" * 65)
        self.stdout.write(self.style.SUCCESS("RUNTIME DIAGNOSTIC COMPLETED PASSING"))
        self.stdout.write("=" * 65 + "\n")
