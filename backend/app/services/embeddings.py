"""
Embedding generation service.
Uses sentence-transformers for semantic embeddings.
"""

import logging
import numpy as np
from typing import List, Tuple
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""

    def __init__(self, model_name: str = settings.embeddings_model):
        self.model_name = model_name
        self.embedding_dim = 384
        self.model = None

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(
                f"Loaded embedding model: {model_name} "
                f"(dimension: {self.embedding_dim})"
            )
        except Exception as e:
            logger.warning(
                f"Sentence-transformers unavailable ({str(e)}). "
                f"Using deterministic feature vector fallback."
            )
            self.model = None

    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Deterministic fallback feature vector generator."""
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        if not text or not text.strip():
            return vec
        words = text.lower().split()
        for w in words:
            idx = abs(hash(w)) % self.embedding_dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        """
        try:
            if not text or not text.strip():
                return np.zeros(self.embedding_dim)

            if self.model is None:
                return self._fallback_embedding(text)

            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return self._fallback_embedding(text)

    def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 32
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.
        """
        try:
            if not texts:
                return []

            if self.model is None:
                return [self._fallback_embedding(t) for t in texts]

            non_empty_texts = [t for t in texts if t and t.strip()]
            if not non_empty_texts:
                return [np.zeros(self.embedding_dim) for _ in texts]

            # Generate embeddings with batching
            embeddings = self.model.encode(
                non_empty_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            return [np.zeros(self.embedding_dim) for _ in texts]

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(max(0, min(1, (similarity + 1) / 2)))  # Normalize to [0, 1]
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def similarities_batch(
        self, query_embedding: np.ndarray, embeddings: List[np.ndarray]
    ) -> List[float]:
        """
        Calculate similarity between query and multiple embeddings efficiently.
        
        Args:
            query_embedding: Query embedding vector
            embeddings: List of document embeddings
            
        Returns:
            List of similarity scores
        """
        try:
            if not embeddings:
                return []

            # Vectorized similarity calculation
            embeddings_array = np.array(embeddings)
            
            # Normalize vectors
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                return [0.0] * len(embeddings)

            embeddings_norms = np.linalg.norm(embeddings_array, axis=1)
            
            # Avoid division by zero
            embeddings_norms[embeddings_norms == 0] = 1

            # Cosine similarity
            dot_products = np.dot(embeddings_array, query_embedding)
            similarities = dot_products / (embeddings_norms * query_norm)

            # Normalize to [0, 1]
            similarities = (similarities + 1) / 2
            similarities = np.clip(similarities, 0, 1)

            return similarities.tolist()
        except Exception as e:
            logger.error(f"Error calculating batch similarities: {str(e)}")
            return [0.0] * len(embeddings)

    def get_embedding_dimension(self) -> int:
        """Get dimension of embeddings generated by this model."""
        return self.embedding_dim
