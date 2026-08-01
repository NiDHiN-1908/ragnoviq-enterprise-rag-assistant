"""
Vector database service using FAISS for similarity search.
Handles storing, retrieving, and searching embeddings.
"""

import logging
import numpy as np
import json
import os
from typing import List, Tuple, Optional
from pathlib import Path
import faiss
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FAISSVectorDB:
    """FAISS-based vector database for similarity search."""

    def __init__(self, vector_db_path: str = settings.vector_db_path, dimension: int = 384):
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.index_file = self.vector_db_path / "index.faiss"
        self.metadata_file = self.vector_db_path / "metadata.json"
        self.index = None
        self.metadata = {}
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load index: {str(e)}, creating new one")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        # Use IVF index for better performance with large datasets
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = {}
        logger.info("Created new FAISS index")

    def add_vectors(
        self, vectors: np.ndarray, metadata: List[dict], website_id: str
    ) -> List[str]:
        """
        Add vectors to the index.
        
        Args:
            vectors: Numpy array of embeddings (N x D)
            metadata: List of metadata dicts for each vector
            website_id: Website ID for filtering
            
        Returns:
            List of vector IDs
        """
        if vectors.shape[0] == 0:
            return []

        try:
            # Convert to float32 if needed
            vectors = vectors.astype(np.float32)
            
            start_id = self.index.ntotal
            self.index.add(vectors)

            # Store metadata
            vector_ids = []
            for i, meta in enumerate(metadata):
                vector_id = str(start_id + i)
                meta["vector_id"] = vector_id
                meta["website_id"] = website_id
                meta["_vector"] = vectors[i].tolist()
                self.metadata[vector_id] = meta
                vector_ids.append(vector_id)

            self._save_index()
            logger.info(f"Added {len(vectors)} vectors to index")
            return vector_ids

        except Exception as e:
            logger.error(f"Error adding vectors: {str(e)}")
            return []

    def search(
        self, query_vector: np.ndarray, top_k: int = 5, website_id: Optional[str] = None
    ) -> List[Tuple[str, float, dict]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            website_id: Optional filter by website
            
        Returns:
            List of (vector_id, distance, metadata) tuples
        """
        try:
            if self.index.ntotal == 0:
                return []

            query_vector = np.array([query_vector], dtype=np.float32)
            distances, indices = self.index.search(query_vector, min(top_k * 4, self.index.ntotal))

            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < 0:
                    continue
                vector_id = str(idx)
                if vector_id not in self.metadata:
                    continue

                meta = self.metadata[vector_id]
                
                # Filter by website if specified
                if website_id and meta.get("website_id") != website_id:
                    continue

                # Convert L2 distance to similarity score in [0, 1]
                similarity = float(1 / (1 + distance))
                clean_meta = {k: v for k, v in meta.items() if k != "_vector"}
                
                results.append((vector_id, similarity, clean_meta))

                if len(results) >= top_k:
                    break

            return results

        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
            return []

    def delete_vectors(self, website_id: str) -> int:
        """
        Delete all vectors for a website and rebuild index cleanly.
        
        Args:
            website_id: Website ID to delete
            
        Returns:
            Number of vectors deleted
        """
        try:
            # Get IDs to delete
            ids_to_delete = [
                vid for vid, meta in self.metadata.items()
                if meta.get("website_id") == website_id
            ]

            if not ids_to_delete:
                return 0

            # Remove from metadata
            for vid in ids_to_delete:
                del self.metadata[vid]

            # Rebuild index with remaining vectors
            remaining_vids = list(self.metadata.keys())
            self.index = faiss.IndexFlatL2(self.dimension)
            new_metadata = {}

            if remaining_vids:
                remaining_vectors = []
                for new_id, old_vid in enumerate(remaining_vids):
                    meta = self.metadata[old_vid]
                    vec = meta.get("_vector")
                    if vec:
                        remaining_vectors.append(vec)
                    meta["vector_id"] = str(new_id)
                    new_metadata[str(new_id)] = meta

                if remaining_vectors:
                    vec_array = np.array(remaining_vectors, dtype=np.float32)
                    self.index.add(vec_array)

            self.metadata = new_metadata
            self._save_index()
            logger.info(f"Deleted {len(ids_to_delete)} vectors for website {website_id}. Rebuilt FAISS index with {self.index.ntotal} vectors.")
            return len(ids_to_delete)

        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            return 0

    def _save_index(self):
        """Save index and metadata to disk."""
        try:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f)
            logger.debug("Saved FAISS index to disk")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")

    def get_stats(self) -> dict:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "metadata_entries": len(self.metadata),
            "index_file_size_mb": (
                self.index_file.stat().st_size / 1024 / 1024
                if self.index_file.exists()
                else 0
            ),
        }

    def clear(self):
        """Clear entire index and metadata."""
        self._create_new_index()
        self.metadata = {}
        self._save_index()
        logger.info("Cleared FAISS index")
