import os
import sys
import time
import io
import django
from PIL import Image, ImageDraw, ImageFont

# Setup Django Environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')
django.setup()

from core.ai_engine.providers.local_offline_vision import LocalOfflineVisionProvider

def run_test():
    print("==================================================")
    print("INTELLIGRADE: LOCAL OLLAMA (MOONDREAM) TEST")
    print("==================================================")

    # 1. Create a sample test image with clear text
    img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(50, 50), (1150, 750)], outline=(0, 0, 0), width=3)
    draw.text((100, 100), "Ans to Question No 1", fill=(0, 0, 0))
    draw.text((100, 200), "Mathematical Formulation: f(x) = 2x + 5", fill=(0, 0, 0))
    draw.text((100, 300), "Conclusion: Verified with diagram.", fill=(0, 0, 0))

    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=95)
    img_bytes = img_buffer.getvalue()

    print(f"Sample test image generated ({len(img_bytes)} bytes, 1200x800 px).")

    # 2. Instantiate LocalOfflineVisionProvider
    provider = LocalOfflineVisionProvider(model_name="moondream")
    print(f"Provider initialized: {provider.__class__.__name__} (Model: {provider.model_name}, Endpoint: {provider.endpoint})")

    # 3. Benchmark inference
    start_t = time.time()
    prompt = "Transcribe the text in this image concisely."
    print(f"Sending request with 800px downscaled payload (timeout=35.0s)...")

    try:
        response = provider.generate_completion(
            prompt=prompt,
            image_bytes=img_bytes,
            timeout=35.0
        )
        elapsed = time.time() - start_t
        print(f"\n[SUCCESS] Response received in {elapsed:.2f} seconds:")
        print("--------------------------------------------------")
        print(response)
        print("--------------------------------------------------")
        print(f"CPU Latency Benchmark: {elapsed:.2f}s (Budget: 35.0s)")
    except Exception as e:
        elapsed = time.time() - start_t
        print(f"\n[EXCEPTION / OFFLINE] {e} (after {elapsed:.2f}s)")
        print("Note: If Ollama daemon is not running on 127.0.0.1:11434, start it with `ollama run moondream`.")

if __name__ == "__main__":
    run_test()
