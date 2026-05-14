"""
Main orchestration service for the RAG pipeline.
Coordinates crawling, parsing, chunking, embedding, and indexing.
"""

import logging
import asyncio
from typing import Optional, List
from datetime import datetime
from app.services.crawler import WebCrawler
from app.services.chunker import TextChunker
from app.services.retriever import RAGRetriever
from app.utils.parser import ContentParser
from app.db.database import SessionLocal
from app.db.repositories import (
    WebsiteRepository,
    WebPageRepository,
    TextChunkRepository,
    IngestionTaskRepository,
)

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates the complete RAG ingestion pipeline."""

    def __init__(self):
        self.crawler = WebCrawler()
        self.chunker = TextChunker()
        self.parser = ContentParser()
        self.retriever = RAGRetriever()

    def ingest_website(self, website_url: str, website_title: Optional[str] = None) -> str:
        """
        Main entry point for website ingestion.
        
        Args:
            website_url: URL to crawl
            website_title: Optional custom title
            
        Returns:
            Website ID
        """
        db = SessionLocal()
        try:
            # Check if website already exists
            existing = WebsiteRepository.get_by_url(db, website_url)
            if existing:
                logger.warning(f"Website already exists: {website_url}")
                return existing.id

            # Create website record
            website = WebsiteRepository.create(
                db, url=website_url, title=website_title
            )
            logger.info(f"Created website record: {website.id}")

            # Execute pipeline steps
            self._execute_pipeline(db, website.id, website_url)

            return website.id

        except Exception as e:
            logger.error(f"Error in ingestion pipeline: {str(e)}")
            raise
        finally:
            db.close()

    def _execute_pipeline(self, db, website_id: str, website_url: str):
        """Execute the full ingestion pipeline."""
        try:
            # Step 1: Crawl website
            logger.info(f"Starting crawl for website: {website_id}")
            WebsiteRepository.update_status(db, website_id, "indexing")

            pages = self._crawl_and_parse(website_url, website_id, db)
            logger.info(f"Crawled and parsed {len(pages)} pages")

            if not pages:
                WebsiteRepository.update_status(db, website_id, "failed")
                return

            # Step 2: Chunk documents
            logger.info(f"Chunking {len(pages)} pages")
            all_chunks = self._chunk_documents(pages, website_id, db)
            logger.info(f"Created {len(all_chunks)} chunks")

            if not all_chunks:
                WebsiteRepository.update_status(db, website_id, "failed")
                return

            # Step 3: Generate embeddings and index
            logger.info(f"Indexing {len(all_chunks)} chunks")
            self._index_chunks(all_chunks, website_id)

            # Step 4: Update metadata
            WebsiteRepository.update_crawl_metadata(
                db, website_id, len(pages), len(all_chunks)
            )
            WebsiteRepository.update_status(db, website_id, "indexed")

            logger.info(f"Ingestion complete for website: {website_id}")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            WebsiteRepository.update_status(db, website_id, "failed")
            raise

    def _crawl_and_parse(self, url: str, website_id: str, db) -> List[dict]:
        """Crawl website and parse content."""
        try:
            pages = self.crawler.crawl(url)

            parsed_pages = []
            for page in pages:
                # Store page in DB
                web_page = WebPageRepository.create(
                    db,
                    website_id=website_id,
                    url=page["url"],
                    title=page.get("title"),
                    content_raw=page["content"],
                )

                # Parse content
                cleaned_content = self.parser.parse_html(page["content"])
                word_count = len(cleaned_content.split())

                # Update page with cleaned content
                WebPageRepository.update(
                    db,
                    web_page.id,
                    content_cleaned=cleaned_content,
                    word_count=word_count,
                )

                parsed_pages.append({
                    "page_id": web_page.id,
                    "url": page["url"],
                    "title": page.get("title"),
                    "content": cleaned_content,
                    "word_count": word_count,
                })

            return parsed_pages

        except Exception as e:
            logger.error(f"Error in crawl and parse: {str(e)}")
            return []

    def _chunk_documents(self, pages: List[dict], website_id: str, db) -> List[dict]:
        """Chunk pages into smaller pieces."""
        try:
            all_chunks = []

            for page in pages:
                # Chunk page content
                chunks = self.chunker.chunk_text(
                    page["content"],
                    metadata={
                        "page_id": page["page_id"],
                        "page_url": page["url"],
                        "page_title": page["title"],
                        "website_id": website_id,
                    },
                )

                # Store chunks in DB
                chunk_data = []
                for chunk in chunks:
                    chunk_data.append({
                        "website_id": website_id,
                        "page_id": page["page_id"],
                        "content": chunk["content"],
                        "chunk_index": chunk["chunk_index"],
                        "start_char": chunk["start_char"],
                        "end_char": chunk["end_char"],
                    })

                TextChunkRepository.bulk_create(db, chunk_data)

                # Prepare for indexing
                for i, chunk in enumerate(chunks):
                    all_chunks.append({
                        "content": chunk["content"],
                        "chunk_index": i,
                        "page_id": page["page_id"],
                        "page_url": page["url"],
                        "page_title": page["title"],
                        "website_id": website_id,
                    })

            return all_chunks

        except Exception as e:
            logger.error(f"Error in chunking: {str(e)}")
            return []

    def _index_chunks(self, chunks: List[dict], website_id: str):
        """Generate embeddings and add to vector DB."""
        try:
            # Add to retriever (generates embeddings internally)
            chunk_ids = self.retriever.add_documents(chunks, website_id)
            logger.info(f"Indexed {len(chunk_ids)} chunks")

        except Exception as e:
            logger.error(f"Error in indexing: {str(e)}")
            raise

    def delete_website(self, website_id: str):
        """Delete a website and all its data."""
        db = SessionLocal()
        try:
            # Delete from vector DB
            self.retriever.delete_website(website_id)

            # Delete from relational DB
            WebsiteRepository.delete(db, website_id)

            logger.info(f"Deleted website: {website_id}")

        finally:
            db.close()

    def get_ingestion_status(self, website_id: str) -> dict:
        """Get current ingestion status."""
        db = SessionLocal()
        try:
            website = WebsiteRepository.get_by_id(db, website_id)
            if not website:
                return {}

            return {
                "website_id": website.id,
                "url": website.url,
                "status": website.status,
                "total_pages": website.total_pages,
                "total_chunks": website.total_chunks,
                "last_crawled": website.last_crawled,
            }

        finally:
            db.close()
