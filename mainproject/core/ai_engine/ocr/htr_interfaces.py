from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class HTRResult:
    """
    Standardized data contract representing handwritten text recognition (HTR) output.
    """
    text: str
    confidence: float
    engine_name: str
    latency_seconds: float
    bounding_boxes: Optional[List[List[int]]] = field(default_factory=list)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "engine_name": self.engine_name,
            "latency_seconds": self.latency_seconds,
            "bounding_boxes": self.bounding_boxes,
            "raw_metadata": self.raw_metadata,
        }


class BaseHandwritingRecognizer(ABC):
    """
    Abstract Base Class for isolated HTR Model Adapters.
    Encapsulates model loading, single crop prediction, and batch processing.
    """

    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.is_initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Loads weights, allocates compute resources, and prepares inference pipeline.
        Returns True on successful initialization.
        """
        pass

    @abstractmethod
    def predict_crop(self, image_input: Any) -> HTRResult:
        """
        Executes handwriting recognition on a single image crop (path, bytes, PIL Image, or ndarray).
        Returns a standardized HTRResult object.
        """
        pass

    @abstractmethod
    def batch_predict(self, image_inputs: List[Any]) -> List[HTRResult]:
        """
        Executes handwriting recognition across a list/batch of image crops.
        Returns a list of HTRResult objects.
        """
        pass
