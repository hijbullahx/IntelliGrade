import io
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
from PIL import Image

from .runtime_config import detect_runtime_environment, get_env_value, is_cuda_available

_easyocr_reader_instance = None
_easyocr_lock = threading.Lock()


def _get_default_easyocr_model_directory() -> str:
    return str(Path.home() / '.EasyOCR' / 'model')


def _get_default_easyocr_user_directory() -> str:
    return str(Path.home() / '.EasyOCR' / 'user_network')


def get_easyocr_cpu_threads() -> int:
    raw_value = get_env_value('EASYOCR_CPU_THREADS', default='1')
    try:
        return max(1, int(raw_value))
    except Exception:
        return 1


def get_easyocr_max_dimension() -> Optional[int]:
    raw_value = get_env_value('EASYOCR_MAX_DIMENSION')
    if raw_value:
        try:
            return max(0, int(raw_value)) or None
        except Exception:
            return None

    if detect_runtime_environment() == 'CODESPACES' and not is_cuda_available():
        return 1024

    return None


def prepare_easyocr_image(image_input: Any, max_dimension: Optional[int] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Loads an OCR input image and optionally downscales it for CPU-friendly EasyOCR."""
    if max_dimension is None:
        max_dimension = get_easyocr_max_dimension()

    if isinstance(image_input, (str, os.PathLike)):
        pil_image = Image.open(image_input)
    elif isinstance(image_input, (bytes, bytearray)):
        pil_image = Image.open(io.BytesIO(image_input))
    else:
        pil_image = Image.fromarray(np.asarray(image_input))

    pil_image = pil_image.convert('RGB')
    original_size = pil_image.size
    resized = False

    if max_dimension and max(original_size) > max_dimension:
        scale_ratio = float(max_dimension) / float(max(original_size))
        working_size = (
            max(1, int(round(original_size[0] * scale_ratio))),
            max(1, int(round(original_size[1] * scale_ratio))),
        )
        pil_image = pil_image.resize(working_size, Image.Resampling.LANCZOS)
        resized = True

    return np.asarray(pil_image), {
        'original_size': original_size,
        'working_size': pil_image.size,
        'resized': resized,
        'max_dimension': max_dimension,
    }

def get_ocr_reader(lang_list: Optional[list] = None) -> Any:
    """
    Lazy-loaded, thread-safe EasyOCR Reader singleton.
    Prevents repeatedEasyOCR initialization across views and pipeline services.
    Auto-detects CUDA GPU availability safely.
    """
    global _easyocr_reader_instance
    if lang_list is None:
        lang_list = ['en']

    if _easyocr_reader_instance is None:
        with _easyocr_lock:
            if _easyocr_reader_instance is None:
                try:
                    import easyocr
                    import torch
                    use_gpu = is_cuda_available()
                    if not use_gpu:
                        try:
                            torch.set_num_threads(get_easyocr_cpu_threads())
                            torch.set_num_interop_threads(1)
                        except Exception:
                            pass
                    print(f"[OCR ENGINE INITIALIZATION] Loading EasyOCR Reader (languages={lang_list}, GPU={use_gpu})...")
                    _easyocr_reader_instance = easyocr.Reader(
                        lang_list,
                        gpu=use_gpu,
                        model_storage_directory=get_env_value('EASYOCR_MODEL_STORAGE_DIRECTORY', default=_get_default_easyocr_model_directory()),
                        user_network_directory=get_env_value('EASYOCR_MODULE_PATH', default=_get_default_easyocr_user_directory()),
                    )
                except Exception as e:
                    print(f"[OCR ENGINE INITIALIZATION WARNING] Could not initialize EasyOCR with GPU={is_cuda_available()}: {e}")
                    try:
                        import easyocr
                        import torch
                        try:
                            torch.set_num_threads(get_easyocr_cpu_threads())
                            torch.set_num_interop_threads(1)
                        except Exception:
                            pass
                        _easyocr_reader_instance = easyocr.Reader(
                            lang_list,
                            gpu=False,
                            model_storage_directory=get_env_value('EASYOCR_MODEL_STORAGE_DIRECTORY', default=_get_default_easyocr_model_directory()),
                            user_network_directory=get_env_value('EASYOCR_MODULE_PATH', default=_get_default_easyocr_user_directory()),
                        )
                    except Exception as e2:
                        print(f"[OCR ENGINE CRITICAL] EasyOCR CPU fallback failed: {e2}")
                        return None
    return _easyocr_reader_instance

class OCRConfig:
    DEFAULT_DPI = 300
    PREPROCESS_ENABLED = True
    CONTRAST_ENHANCEMENT = True
    DESKEW_ENABLED = True

def get_ocr_config() -> Dict[str, Any]:
    return {
        "dpi": OCRConfig.DEFAULT_DPI,
        "gpu_accelerated": is_cuda_available(),
        "easyocr_ready": get_ocr_reader() is not None,
    }
