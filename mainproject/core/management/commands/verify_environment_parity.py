import sys
import platform
import django
from django.core.management.base import BaseCommand
from django.conf import settings
from config import get_config_fingerprint
from config.runtime_config import detect_runtime_environment, is_cuda_available
from config.ai_config import get_ai_config

class Command(BaseCommand):
    help = 'Asserts cross-environment runtime and configuration parity across Local, Codespaces, and Production.'

    def handle(self, *args, **options):
        self.stdout.write("=" * 65)
        self.stdout.write("        INTELLIGRADE CROSS-ENVIRONMENT PARITY VERIFIER")
        self.stdout.write("=" * 65)

        env_name = detect_runtime_environment()
        fingerprints = get_config_fingerprint()
        ai_info = get_ai_config()

        self.stdout.write(f"\n[ENVIRONMENT METADATA]")
        self.stdout.write(f"Target Environment : {env_name}")
        self.stdout.write(f"Python             : {sys.version.split()[0]}")
        self.stdout.write(f"Django             : {django.get_version()}")
        self.stdout.write(f"Timezone           : {settings.TIME_ZONE}")

        self.stdout.write(f"\n[PARITY CHECKPOINTS]")

        # 1. Config Versions
        v_ok = all(v == "3.0" for v in fingerprints.values())
        self.stdout.write(f"1. Configuration Version Fingerprints : {'PASS' if v_ok else 'FAIL'}")

        # 2. AI Provider Configuration
        ai_ok = ai_info['gemini_configured'] or ai_info['groq_configured'] or ai_info['openai_configured']
        self.stdout.write(f"2. AI Provider API Configuration      : {'PASS (Provider Ready)' if ai_ok else 'WARNING (Missing Keys)'}")

        # 3. PyMuPDF Renderer Availability
        try:
            import fitz
            pdf_ok = True
        except ImportError:
            pdf_ok = False
        self.stdout.write(f"3. PyMuPDF PDF Stream Renderer        : {'PASS' if pdf_ok else 'FAIL'}")

        # 4. EasyOCR Reader Acceleration / Fallback
        try:
            from config.ocr_config import get_ocr_reader, is_easyocr_enabled
            if is_easyocr_enabled():
                ocr_ready = get_ocr_reader() is not None
                ocr_status = 'PASS (Enabled & Ready)' if ocr_ready else 'FAIL'
            else:
                ocr_status = 'DISABLED (Safe for Passenger/cPanel)'
        except Exception:
            ocr_status = 'FAIL'
        self.stdout.write(f"4. EasyOCR Reader Singleton           : {ocr_status}")

        # 5. Media & Static Directories
        media_ok = bool(settings.MEDIA_ROOT) and bool(settings.MEDIA_URL)
        self.stdout.write(f"5. Media & Static Directory Resolvers : {'PASS' if media_ok else 'FAIL'}")

        self.stdout.write("\n" + "=" * 65)
        if v_ok and pdf_ok and media_ok:
            self.stdout.write(self.style.SUCCESS("CROSS-ENVIRONMENT PARITY VERIFICATION PASSED"))
        else:
            self.stdout.write(self.style.ERROR("CROSS-ENVIRONMENT PARITY VERIFICATION FAILED"))
        self.stdout.write("=" * 65 + "\n")
