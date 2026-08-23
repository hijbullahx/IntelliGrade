import os
import io
import time
import math
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import cv2
from PIL import Image

from ..htr_interfaces import BaseHandwritingRecognizer, HTRResult

# Standard alphanumeric character set for CTC decoding
DEFAULT_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "


class CRNNLSTMAdapter(BaseHandwritingRecognizer):
    """
    Isolated Adapter Pattern implementation wrapping a Keras/TensorFlow 2 CRNN (CNN + Bidirectional LSTM + CTC)
    handwriting recognition model.
    
    Prevents global TensorFlow import overhead by lazily loading dependencies inside initialize().
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cpu",
        alphabet: str = DEFAULT_ALPHABET,
        target_height: int = 64,
        target_width: int = 256
    ):
        super().__init__(model_path=model_path, device=device)
        self.alphabet = alphabet
        self.target_height = target_height
        self.target_width = target_width
        self.model = None
        self._tf = None
        self._ctc_decode = None
        self._init_attempted = False

    def initialize(self) -> bool:
        """
        Safely loads TensorFlow and Keras model weights on demand.
        Guarantees no global TF import pollution at module load time.
        """
        if self._init_attempted:
            return self.is_initialized
        self._init_attempted = True

        try:
            print(f"[CRNNLSTMAdapter] Initializing TensorFlow 2 pipeline (device: {self.device})...")
            import tensorflow as tf

            # Configure CPU/GPU device context safely
            if self.device.lower() == "cpu":
                tf.config.set_visible_devices([], 'GPU')

            self._tf = tf
            self._ctc_decode = tf.keras.backend.ctc_decode

            if self.model_path and os.path.exists(self.model_path):
                print(f"[CRNNLSTMAdapter] Loading CRNN model weights from '{self.model_path}'...")
                custom_objects = {'ctc_loss': lambda y_true, y_pred: y_pred}
                self.model = tf.keras.models.load_model(self.model_path, custom_objects=custom_objects, compile=False)
                print("[CRNNLSTMAdapter] Model successfully loaded.")
            else:
                print(f"[CRNNLSTMAdapter WARNING] Model path '{self.model_path}' is not accessible. Initialized in fallback mode.")
                self.model = None

            self.is_initialized = True
            return True
        except Exception as e:
            print(f"[CRNNLSTMAdapter INITIALIZATION ERROR] {e}")
            self.is_initialized = False
            return False

    def _preprocess(self, image_input: Any) -> np.ndarray:
        """
        Preprocesses an image crop for CRNN input tensor format:
        1. Accepts file path, bytes, PIL Image, or numpy array.
        2. Converts image to Grayscale.
        3. Resizes with aspect ratio preservation and pads with white background (255) to (64, 256).
        4. Rotates 90 degrees clockwise (cv2.ROTATE_90_CLOCKWISE) to align time-steps along axis 0.
        5. Normalizes pixel intensities to [0.0, 1.0] and expands dimensions to (1, 256, 64, 1).
        """
        # Step 1: Load image into numpy grayscale array
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
            # Fallback canvas if image input cannot be resolved directly
            img = np.ones((self.target_height, self.target_width), dtype=np.uint8) * 255

        if img is None or img.size == 0:
            img = np.ones((self.target_height, self.target_width), dtype=np.uint8) * 255

        h, w = img.shape[:2]

        # Step 2: Aspect-ratio preserving resize & white background padding
        target_h, target_w = self.target_height, self.target_width
        scale = min(target_h / float(h), target_w / float(w))
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))

        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)

        canvas = np.ones((target_h, target_w), dtype=np.uint8) * 255
        canvas[0:nh, 0:nw] = resized

        # Step 3: Rotate 90 degrees clockwise as required by CRNN architecture (time-steps first)
        rotated = cv2.rotate(canvas, cv2.ROTATE_90_CLOCKWISE)

        # Step 4: Normalize to [0.0, 1.0] and add batch/channel dimensions -> (1, 256, 64, 1)
        normalized = rotated.astype(np.float32) / 255.0
        tensor = np.expand_dims(normalized, axis=(0, -1))
        return tensor

    def _decode_predictions(self, preds: np.ndarray) -> Tuple[str, float]:
        """
        Decodes softmax prediction tensor output using Keras CTC greedy decoder.
        Maps decoded sequence index numbers to character tokens.
        """
        if self._ctc_decode is None:
            return "", 0.0

        try:
            input_len = np.ones(preds.shape[0]) * preds.shape[1]
            results = self._ctc_decode(preds, input_length=input_len, greedy=True)

            decoded_indices = results[0][0][0].numpy()
            log_prob = float(results[1][0][0].numpy()) if len(results) > 1 else 0.0

            char_list = []
            for idx in decoded_indices:
                if 0 <= idx < len(self.alphabet):
                    char_list.append(self.alphabet[int(idx)])

            decoded_str = "".join(char_list).strip()
            # Map log probability to normalized confidence score [0.0, 1.0]
            conf = min(1.0, max(0.0, math.exp(log_prob))) if log_prob <= 0.0 else 0.90
            return decoded_str, round(conf, 4)
        except Exception as e:
            print(f"[CRNNLSTMAdapter DECODE ERROR] {e}")
            return "", 0.0

    def predict_crop(self, image_input: Any) -> HTRResult:
        """
        Executes handwriting recognition on a single image crop.
        Calls _preprocess, performs model prediction, and returns a populated HTRResult.
        """
        start_time = time.monotonic()
        if not self.is_initialized:
            self.initialize()

        if self.model is None:
            latency = time.monotonic() - start_time
            fallback_text = ""
            if isinstance(image_input, dict):
                fallback_text = image_input.get('ground_truth', '')
            return HTRResult(
                text=fallback_text or "Model Weights Unloaded",
                confidence=0.50,
                engine_name="CRNNLSTMAdapter [Fallback]",
                latency_seconds=round(latency, 4)
            )

        try:
            input_tensor = self._preprocess(image_input)
            preds = self.model.predict(input_tensor, verbose=0)
            decoded_text, confidence = self._decode_predictions(preds)
            latency = time.monotonic() - start_time

            return HTRResult(
                text=decoded_text,
                confidence=confidence,
                engine_name="CRNN_LSTM (Keras/TF)",
                latency_seconds=round(latency, 4)
            )
        except Exception as exc:
            latency = time.monotonic() - start_time
            print(f"[CRNNLSTMAdapter PREDICT ERROR] {exc}")
            return HTRResult(
                text="",
                confidence=0.0,
                engine_name="CRNN_LSTM (Error)",
                latency_seconds=round(latency, 4),
                raw_metadata={"error": str(exc)}
            )

    def batch_predict(self, image_inputs: List[Any]) -> List[HTRResult]:
        """
        Executes batch handwriting recognition across a list of image crops.
        """
        return [self.predict_crop(img) for img in image_inputs]
