from __future__ import annotations

import faulthandler
import json
import os
import platform
import resource
import signal
import sys
import time
from pathlib import Path


faulthandler.enable(all_threads=True)


def print_banner(title: str) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)


def log_resource(prefix: str) -> None:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(
        f"{prefix} | pid={os.getpid()} | rss_mb={usage.ru_maxrss / 1024:.1f} | "
        f"user_s={usage.ru_utime:.2f} | sys_s={usage.ru_stime:.2f}"
    )


def signal_handler(signum, frame):
    print(f"[SIGNAL RECEIVED] signum={signum}")
    log_resource("[SIGNAL RESOURCE]")
    raise SystemExit(128 + signum)


for _signum in (signal.SIGTERM, signal.SIGINT, signal.SIGABRT):
    try:
        signal.signal(_signum, signal_handler)
    except Exception:
        pass


print_banner("INTELLIGRADE EASYOCR DIAGNOSTIC")
print(f"python_version={sys.version}")
print(f"platform={platform.platform()}")
print(f"executable={sys.executable}")
print(f"cwd={Path.cwd()}")
print(f"home={os.environ.get('HOME')}")
print(f"omp_num_threads={os.environ.get('OMP_NUM_THREADS')}")
print(f"mkl_num_threads={os.environ.get('MKL_NUM_THREADS')}")
print(f"easyocr_model_storage={os.environ.get('EASYOCR_MODEL_STORAGE_DIRECTORY')}")
print(f"easyocr_module_path={os.environ.get('EASYOCR_MODULE_PATH')}")
print(f"torch_home={os.environ.get('TORCH_HOME')}")
log_resource("[START]")

try:
    import torch
    import easyocr
    import cv2
    import numpy as np
    from PIL import Image
except Exception as import_err:
    print(f"[IMPORT FAILURE] {repr(import_err)}")
    raise

print(f"torch_version={torch.__version__}")
print(f"easyocr_version={easyocr.__version__}")
print(f"cv2_version={cv2.__version__}")
print(f"numpy_version={np.__version__}")

print("[TORCH CONFIG]")
print(f"cuda_available={torch.cuda.is_available()}")
print(f"torch_num_threads={torch.get_num_threads()}")
print(f"torch_num_interop_threads={torch.get_num_interop_threads()}")

image_path = Path("request_trace/rendered_page_1.png")
if not image_path.exists():
    raise FileNotFoundError(f"Missing OCR input image: {image_path}")

print(f"[IMAGE EXISTS] {image_path} size={image_path.stat().st_size} bytes")
print("[IMAGE LOAD START]")
image = Image.open(image_path)
print(f"[IMAGE LOAD SUCCESS] size={image.size} mode={image.mode}")
log_resource("[AFTER IMAGE LOAD]")

print("[EASYOCR INIT START]")
init_started = time.monotonic()
reader = easyocr.Reader(['en'], gpu=False)
print(f"[EASYOCR INIT SUCCESS] elapsed_s={time.monotonic() - init_started:.2f}")
log_resource("[AFTER EASYOCR INIT]")

print("[EASYOCR OCR START]")
ocr_started = time.monotonic()
result = reader.readtext(str(image_path))
elapsed = time.monotonic() - ocr_started
print(f"[EASYOCR OCR SUCCESS] elapsed_s={elapsed:.2f}")
print(f"[EASYOCR OCR RESULT COUNT] {len(result)}")

text_parts = [row[1] for row in result]
confidences = [float(row[2]) for row in result]
combined_text = "\n".join(text_parts).strip()
print(f"[TEXT LENGTH] {len(combined_text)}")
print(f"[CONFIDENCE] {sum(confidences) / len(confidences) if confidences else 0.0:.4f}")
print(f"[TEXT PREVIEW] {combined_text[:1000]}")
log_resource("[END]")
