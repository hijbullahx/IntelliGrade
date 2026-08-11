import os
import threading
from typing import Dict, Any, Optional
from .runtime_config import is_cuda_available

_easyocr_reader_instance = None
_easyocr_lock = threading.Lock()

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
                    use_gpu = is_cuda_available()
                    print(f"[OCR ENGINE INITIALIZATION] Loading EasyOCR Reader (languages={lang_list}, GPU={use_gpu})...")
                    _easyocr_reader_instance = easyocr.Reader(lang_list, gpu=use_gpu)
                except Exception as e:
                    print(f"[OCR ENGINE INITIALIZATION WARNING] Could not initialize EasyOCR with GPU={is_cuda_available()}: {e}")
                    try:
                        import easyocr
                        _easyocr_reader_instance = easyocr.Reader(lang_list, gpu=False)
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
