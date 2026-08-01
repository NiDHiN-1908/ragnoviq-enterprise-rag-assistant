import logging
import re
from typing import List, Tuple, Optional, Union
import numpy as np
from app.services.embeddings import EmbeddingGenerator
from app.vector_db.faiss_db import FAISSVectorDB
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGRetriever:
    """Retrieves relevant context for queries using Hybrid RAG search."""

    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = FAISSVectorDB(dimension=self.embedding_generator.embedding_dim)
        self.top_k = settings.top_k_chunks
        self.similarity_threshold = settings.similarity_threshold

    def _calculate_lexical_score(self, query: str, content: str) -> float:
        """Calculate lexical (keyword) match score between query and chunk content."""
        if not query or not content:
            return 0.0
        query_words = set(re.findall(r'\w+', query.lower()))
        content_words = set(re.findall(r'\w+', content.lower()))
        
        if not query_words:
            return 0.0
            
        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)

    def retrieve_context(
        self,
        query: str,
        website_id: Optional[Union[str, List[str]]] = None,
        top_k: Optional[int] = None,
    ) -> List[dict]:
        """
        Retrieve relevant context for a query using hybrid dense + lexical scoring.
        
        Args:
            query: User query
            website_id: Optional filter by website ID or list of website IDs
            top_k: Number of results (uses default if not specified)
            
        Returns:
            List of relevant chunks with relevance scores
        """
        try:
            if not query or not query.strip():
                return []

            target_top_k = top_k or self.top_k
            query_embedding = self.embedding_generator.generate_embedding(query)

            # Support list of website IDs or single website ID
            allowed_websites = None
            if isinstance(website_id, list):
                allowed_websites = set(website_id) if website_id else None
            elif isinstance(website_id, str) and website_id:
                allowed_websites = {website_id}

            # Fetch extra candidates from FAISS vector search
            raw_results = self.vector_db.search(
                query_embedding,
                top_k=target_top_k * 3,
                website_id=None,  # We perform website filtering dynamically
            )

            hybrid_results = []
            seen_contents = set()

            for vector_id, vector_sim, metadata in raw_results:
                site_id = metadata.get("website_id")
                if allowed_websites and site_id not in allowed_websites:
                    continue

                content = metadata.get("content", "")
                if not content or content in seen_contents:
                    continue
                seen_contents.add(content)

                # Calculate lexical keyword match score
                lexical_score = self._calculate_lexical_score(query, content)

                # Hybrid score combining dense similarity (70%) and lexical overlap (30%)
                combined_score = (0.7 * float(vector_sim)) + (0.3 * lexical_score)

                hybrid_results.append({
                    "chunk_id": vector_id,
                    "content": content,
                    "page_url": metadata.get("page_url", ""),
                    "page_title": metadata.get("page_title") or "Untitled",
                    "website_id": site_id,
                    "similarity_score": float(combined_score),
                    "vector_score": float(vector_sim),
                    "lexical_score": float(lexical_score),
                    "chunk_index": metadata.get("chunk_index", 0),
                })

            # Sort by hybrid combined score descending
            hybrid_results.sort(key=lambda x: x["similarity_score"], reverse=True)

            # Filter by similarity threshold with fallback floor
            filtered_context = [
                item for item in hybrid_results if item["similarity_score"] >= self.similarity_threshold
            ]

            # Fallback floor: if strict threshold yielded nothing, retain top items above 0.15 score
            if not filtered_context and hybrid_results:
                filtered_context = [
                    item for item in hybrid_results if item["similarity_score"] >= 0.15
                ][:target_top_k]
            else:
                filtered_context = filtered_context[:target_top_k]

            logger.info(
                f"Retrieved {len(filtered_context)} relevant chunks for query: '{query[:40]}...'"
            )
            return filtered_context

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []

    def add_documents(self, chunks: List[dict], website_id: str) -> List[str]:
        """Add document chunks to the retriever."""
        try:
            if not chunks:
                return []

            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings_batch(texts)
            embeddings_array = np.array(embeddings, dtype=np.float32)

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

