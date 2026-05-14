"""
RAG retrieval service for finding relevant context.
Handles semantic search and context retrieval.
"""

import logging
from typing import List, Tuple, Optional
import numpy as np
from app.services.embeddings import EmbeddingGenerator
from app.vector_db.faiss_db import FAISSVectorDB
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGRetriever:
    """Retrieves relevant context for queries using RAG."""

    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = FAISSVectorDB(dimension=self.embedding_generator.embedding_dim)
        self.top_k = settings.top_k_chunks
        self.similarity_threshold = settings.similarity_threshold

    def retrieve_context(
        self,
        query: str,
        website_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[dict]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            website_id: Optional filter by website
            top_k: Number of results (uses default if not specified)
            
        Returns:
            List of relevant chunks with scores
        """
        try:
            if not query or not query.strip():
                return []

            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)

            # Search vector DB
            top_k = top_k or self.top_k
            results = self.vector_db.search(
                query_embedding,
                top_k=top_k,
                website_id=website_id,
            )

            # Format results
            context_items = []
            for vector_id, similarity, metadata in results:
                if similarity >= self.similarity_threshold:
                    context_items.append({
                        "chunk_id": vector_id,
                        "content": metadata.get("content", ""),
                        "page_url": metadata.get("page_url", ""),
                        "page_title": metadata.get("page_title"),
                        "website_id": metadata.get("website_id"),
                        "similarity_score": float(similarity),
                        "chunk_index": metadata.get("chunk_index", 0),
                    })

            logger.info(
                f"Retrieved {len(context_items)} relevant chunks for query "
                f"(similarity threshold: {self.similarity_threshold})"
            )
            return context_items

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []

    def add_documents(self, chunks: List[dict], website_id: str) -> List[str]:
        """
        Add document chunks to the retriever.
        
        Args:
            chunks: List of text chunks with metadata
            website_id: Website ID
            
        Returns:
            List of chunk IDs
        """
        try:
            if not chunks:
                return []

            # Extract texts and generate embeddings
            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings_batch(texts)

            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Add to vector DB
            chunk_ids = self.vector_db.add_vectors(embeddings_array, chunks, website_id)

            logger.info(f"Added {len(chunk_ids)} chunks to retriever")
            return chunk_ids

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return []

    def delete_website(self, website_id: str) -> int:
        """Delete all chunks for a website."""
        try:
            deleted = self.vector_db.delete_vectors(website_id)
            logger.info(f"Deleted {deleted} chunks for website {website_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting website: {str(e)}")
            return 0

    def get_stats(self) -> dict:
        """Get retriever statistics."""
        return self.vector_db.get_stats()
