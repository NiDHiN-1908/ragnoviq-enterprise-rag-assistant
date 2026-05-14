"""
Text chunking service with semantic awareness.
Creates overlapping chunks optimized for embedding and retrieval.
"""

import logging
from typing import List
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TextChunker:
    """Handles semantic text chunking."""

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = chunk_size // 4  # Minimum chunk size

    def chunk_text(self, text: str, metadata: dict = None) -> List[dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Metadata about the text (page_id, url, etc.)
            
        Returns:
            List of chunks with metadata
        """
        if not text or len(text.strip()) == 0:
            return []

        # First pass: split by paragraphs/sentences
        chunks = self._semantic_split(text)

        # Second pass: merge small chunks
        chunks = self._merge_small_chunks(chunks)

        # Third pass: add overlap and format
        formatted_chunks = self._add_overlap_and_format(chunks, metadata)

        return formatted_chunks

    def _semantic_split(self, text: str) -> List[str]:
        """
        Attempt semantic splitting by:
        1. Splitting on double newlines (paragraphs)
        2. Then splitting on periods/sentences
        3. Finally splitting on character limit
        """
        # Split by double newlines
        paragraphs = text.split("\n\n")

        chunks = []
        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                chunks.append(paragraph)
            else:
                # Split paragraph by sentences
                sentences = paragraph.split(". ")
                current_chunk = ""

                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 2 <= self.chunk_size:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "

                if current_chunk:
                    chunks.append(current_chunk.strip())

        return chunks

    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """Merge chunks smaller than minimum size."""
        merged = []
        current = ""

        for chunk in chunks:
            combined = current + " " + chunk if current else chunk

            if len(combined) <= self.chunk_size:
                current = combined
            else:
                if current:
                    merged.append(current)
                current = chunk

        if current:
            merged.append(current)

        return merged

    def _add_overlap_and_format(self, chunks: List[str], metadata: dict = None) -> List[dict]:
        """
        Add overlap between chunks and format with metadata.
        """
        formatted_chunks = []
        overlap_text = ""
        char_position = 0

        for idx, chunk in enumerate(chunks):
            # Combine with overlap
            full_chunk = overlap_text + chunk
            start_char = char_position - len(overlap_text)

            formatted_chunks.append({
                "content": full_chunk.strip(),
                "chunk_index": idx,
                "start_char": max(0, start_char),
                "end_char": char_position + len(chunk),
                "metadata": metadata or {},
            })

            # Set overlap for next chunk
            words = chunk.split()
            overlap_words = words[-10:] if len(words) > 10 else words
            overlap_text = " ".join(overlap_words) + " "

            char_position += len(chunk)

        return formatted_chunks

    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of {text, metadata}
            
        Returns:
            List of chunks with source metadata
        """
        all_chunks = []

        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)

        return all_chunks
