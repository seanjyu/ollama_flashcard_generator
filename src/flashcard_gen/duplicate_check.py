from difflib import SequenceMatcher
import numpy as np
import ollama
from .generate import Flashcard, SimilarityMethod


class DuplicateChecker:
    """Check for duplicate flashcards using string or semantic similarity."""

    def __init__(
            self,
            method: SimilarityMethod = SimilarityMethod.STRING,
            string_threshold: float = 0.7,
            semantic_threshold: float = 0.85,
            embedding_model: str = "nomic-embed-text"
    ):
        self.method = method
        self.string_threshold = string_threshold
        self.semantic_threshold = semantic_threshold
        self.embedding_model = embedding_model
        self._embedding_cache: dict[str, list[float]] = {}

    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding with caching."""
        if text not in self._embedding_cache:
            response = ollama.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            self._embedding_cache[text] = response["embedding"]
        return self._embedding_cache[text]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _string_similarity(self, a: str, b: str) -> float:
        """Compute string similarity using SequenceMatcher."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _semantic_similarity(self, a: str, b: str) -> float:
        """Compute semantic similarity using embeddings."""
        emb_a = self._get_embedding(a)
        emb_b = self._get_embedding(b)
        return self._cosine_similarity(emb_a, emb_b)

    def is_duplicate(self, new: Flashcard, existing: list[Flashcard]) -> bool:
        """Check if card is duplicate based on configured method."""
        for card in existing:
            if self.method == SimilarityMethod.STRING:
                if self._string_similarity(new.front, card.front) > self.string_threshold:
                    return True

            elif self.method == SimilarityMethod.SEMANTIC:
                if self._semantic_similarity(new.front, card.front) > self.semantic_threshold:
                    return True

            elif self.method == SimilarityMethod.BOTH:
                if self._string_similarity(new.front, card.front) > self.string_threshold:
                    return True
                if self._semantic_similarity(new.front, card.front) > self.semantic_threshold:
                    return True

        return False

    def clear_cache(self):
        """Clear embedding cache."""
        self._embedding_cache.clear()