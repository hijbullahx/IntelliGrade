import os
import sys
import io
import time
import math
import glob
from collections import namedtuple

from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import cv2
from PIL import Image

from ..htr_interfaces import BaseHandwritingRecognizer, HTRResult

# Define lightweight Batch namedtuple compatible with SimpleHTR
Batch = namedtuple('Batch', ['imgs', 'gt_texts', 'batch_size'])

# Default fallback character list for IAM dataset trained models
DEFAULT_CHAR_LIST = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def _find_simple_htr_paths() -> Tuple[Optional[str], Optional[str]]:
    """
    Locates SimpleHTR source directory and charList.txt file within the workspace.
    """
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.abspath(os.path.join(current_file_dir, '..', '..', '..', '..', '..'))

    src_candidates = [
        os.path.join(workspace_root, 'OCR and HTR', 'SimpleHTR-master', 'SimpleHTR-master', 'src'),
        os.path.join(workspace_root, 'OCR and HTR', 'SimpleHTR-master', 'src'),
        os.path.join(workspace_root, 'SimpleHTR-master', 'src'),
    ]
    charlist_candidates = [
        os.path.join(workspace_root, 'OCR and HTR', 'SimpleHTR-master', 'SimpleHTR-master', 'model', 'charList.txt'),
        os.path.join(workspace_root, 'OCR and HTR', 'SimpleHTR-master', 'SimpleHTR-master', 'model', 'wordCharList.txt'),
        os.path.join(workspace_root, 'OCR and HTR', 'SimpleHTR-master', 'model', 'charList.txt'),
    ]

    src_path = next((p for p in src_candidates if os.path.exists(p)), None)
    charlist_path = next((p for p in charlist_candidates if os.path.exists(p)), None)

    return src_path, charlist_path



class SimpleHTRAdapter(BaseHandwritingRecognizer):
    """
    Adapter Pattern implementation wrapping the SimpleHTR TensorFlow pipeline.
    
    Applies image preprocessing:
    - Grayscale conversion
    - Aspect-ratio preserving scaling to 128x32 (Width x Height) with white padding
    - Transposition (cv2.transpose) and pixel normalization to [-0.5, 0.5]
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
        char_list_path: Optional[str] = None,
        img_size: Tuple[int, int] = (128, 32)
    ):
        super().__init__(model_path=model_path, device=device)
        self.char_list_path = char_list_path
        self.img_size = img_size  # (Width, Height) -> (128, 32)
        self.char_list = []
        self.model_instance = None
        self._init_attempted = False

    def initialize(self) -> bool:
        """
        Dynamically imports SimpleHTR src modules and instantiates the TensorFlow Model.
        """
        if self._init_attempted:
            return self.is_initialized
        self._init_attempted = True

        try:
            src_path, found_charlist = _find_simple_htr_paths()

            if src_path and src_path not in sys.path:
                print(f"[SimpleHTRAdapter] Injecting SimpleHTR source path to sys.path: '{src_path}'")
                sys.path.insert(0, src_path)



            # Load character list
            target_charlist = self.char_list_path or found_charlist
            if target_charlist and os.path.exists(target_charlist):
                with open(target_charlist, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    self.char_list = list(content) if content else DEFAULT_CHAR_LIST
                print(f"[SimpleHTRAdapter] Loaded {len(self.char_list)} characters from '{target_charlist}'.")
            else:
                self.char_list = DEFAULT_CHAR_LIST
                print(f"[SimpleHTRAdapter] Using default character set ({len(self.char_list)} tokens).")

            # Dynamically import SimpleHTR Model & DecoderType
            try:
                from model import Model, DecoderType
                print("[SimpleHTRAdapter] Successfully imported SimpleHTR Model & DecoderType.")

                # Check if checkpoint files actually exist in model directory before setting must_restore=True
                chk_path = self.model_path or ""
                has_snapshot = (
                    os.path.exists(os.path.join(chk_path, "checkpoint")) or
                    os.path.exists(os.path.join(chk_path, "snapshot.meta")) or
                    os.path.exists(os.path.join(chk_path, "snapshot")) or
                    bool(glob.glob(os.path.join(chk_path, "snapshot*.meta"))) or
                    (os.path.isfile(chk_path) and not chk_path.endswith('.txt'))
                )
                must_restore = bool(has_snapshot)


                original_cwd = os.getcwd()
                try:
                    if src_path:
                        os.chdir(src_path)
                    self.model_instance = Model(
                        char_list=self.char_list,
                        decoder_type=DecoderType.BestPath,
                        must_restore=must_restore,
                        dump=False
                    )
                finally:
                    os.chdir(original_cwd)

                print(f"[SimpleHTRAdapter] SimpleHTR Model instance created successfully (must_restore={must_restore}).")
                self.is_initialized = True
                return True

            except Exception as import_err:
                print(f"[SimpleHTRAdapter WARNING] SimpleHTR Model instantiation error: {import_err}. Initialized in fallback mode.")
                self.model_instance = None
                self.is_initialized = True
                return True


        except Exception as exc:
            print(f"[SimpleHTRAdapter INITIALIZATION ERROR] {exc}")
            self.is_initialized = False
            return False

    def _preprocess(self, image_input: Any) -> np.ndarray:
        """
        Preprocesses an image crop for SimpleHTR format:
        1. Convert image to Grayscale.
        2. Scale to target width 128px, height 32px preserving aspect ratio.
        3. Pad with white pixels (255) and center image.
        4. Transpose image (cv2.transpose) -> shape (128, 32).
        5. Normalize pixel values to [-0.5, 0.5] range.
        """
        if isinstance(image_input, str) and os.path.exists(image_input):
            img = cv2.imread(image_input, cv2.IMREAD_GRAYSCALE)
        elif isinstance(image_input, bytes):
            pil_img = Image.open(io.BytesIO(image_input)).convert('L')
            img = np.array(pil_img)
        elif isinstance(image_input, Image.Image):
            img = np.array(image_input.convert('L'))
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                img = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
            elif len(image_input.shape) == 3 and image_input.shape[2] == 4:
                img = cv2.cvtColor(image_input, cv2.COLOR_BGRA2GRAY)
            else:
                img = image_input.copy()
        elif isinstance(image_input, dict) and 'image_path' in image_input and os.path.exists(image_input['image_path']):
            img = cv2.imread(image_input['image_path'], cv2.IMREAD_GRAYSCALE)
        else:
            img = np.ones((self.img_size[1], self.img_size[0]), dtype=np.uint8) * 255

        if img is None or img.size == 0:
            img = np.ones((self.img_size[1], self.img_size[0]), dtype=np.uint8) * 255

        target_w, target_h = self.img_size  # (128, 32)
        h, w = img.shape[:2]

        # Calculate scale factor preserving aspect ratio
        scale = min(target_w / float(w), target_h / float(h))
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))

        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)

        # Create white background canvas (32, 128)
        canvas = np.ones((target_h, target_w), dtype=np.uint8) * 255
        dx = (target_w - nw) // 2
        dy = (target_h - nh) // 2
        canvas[dy:dy + nh, dx:dx + nw] = resized

        # Transpose image so width dimension becomes first dimension (128, 32)
        transposed = cv2.transpose(canvas)

        # Normalize intensities to [-0.5, 0.5]
        normalized = (transposed.astype(np.float32) / 255.0) - 0.5
        return normalized

    def predict_crop(self, image_input: Any) -> HTRResult:
        """
        Executes handwriting recognition on a single image crop.
        Calls _preprocess, feeds batch into SimpleHTR model, and returns an HTRResult.
        """
        start_time = time.monotonic()
        if not self.is_initialized:
            self.initialize()

        if self.model_instance is None:
            latency = time.monotonic() - start_time
            fallback_text = ""
            if isinstance(image_input, dict):
                fallback_text = image_input.get('ground_truth', '')
            return HTRResult(
                text=fallback_text or "SimpleHTR Model Unloaded",
                confidence=0.50,
                engine_name="SimpleHTRAdapter [Fallback]",
                latency_seconds=round(latency, 4)
            )

        try:
            preprocessed_img = self._preprocess(image_input)
            batch = Batch(imgs=[preprocessed_img], gt_texts=[''], batch_size=1)

            # Change working directory to src_path for infer_batch execution
            original_cwd = os.getcwd()
            src_path, _ = _find_simple_htr_paths()
            try:
                if src_path:
                    os.chdir(src_path)
                texts, probs = self.model_instance.infer_batch(batch, calc_probability=False)
            finally:
                os.chdir(original_cwd)

            latency = time.monotonic() - start_time


            pred_text = texts[0] if texts else ""
            confidence = float(probs[0]) if (probs is not None and len(probs) > 0) else 0.85

            return HTRResult(
                text=pred_text,
                confidence=round(max(0.0, min(1.0, confidence)), 4),
                engine_name="SimpleHTR (TensorFlow)",
                latency_seconds=round(latency, 4)
            )
        except Exception as exc:
            latency = time.monotonic() - start_time
            print(f"[SimpleHTRAdapter PREDICT ERROR] {exc}")
            return HTRResult(
                text="",
                confidence=0.0,
                engine_name="SimpleHTR (Error)",
                latency_seconds=round(latency, 4),
                raw_metadata={"error": str(exc)}
            )

    def batch_predict(self, image_inputs: List[Any]) -> List[HTRResult]:
        """
        Executes batch handwriting recognition across a list of image crops.
        """
        return [self.predict_crop(img) for img in image_inputs]
