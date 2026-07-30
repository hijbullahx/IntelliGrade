import math
import re
from typing import List

class EmbeddingEngine:
    """
    Sentence Transformers / Dense Embedding Vector Generator.
    Supports local sentence-transformers models with lightweight TF-IDF n-gram vector fallback.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._st_model = None

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a normalized float vector for the input text.
        """
        try:
            if self._st_model is None:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(self.model_name)
            vector = self._st_model.encode(text).tolist()
            return vector
        except Exception:
            # Fallback 64-dimensional feature hash vector for zero external dependencies
            return self._fallback_hash_vector(text)

    def _fallback_hash_vector(self, text: str, dim: int = 64) -> List[float]:
        tokens = re.findall(r'\w+', text.lower())
        vec = [0.0] * dim
        for tok in tokens:
            idx = abs(hash(tok)) % dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 4) for x in vec]

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return round(dot / (norm1 * norm2), 4)
