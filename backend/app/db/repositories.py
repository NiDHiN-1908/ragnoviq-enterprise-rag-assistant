"""
Database repository for core operations.
Implements repository pattern for data access.
"""

from sqlalchemy.orm import Session
from app.models.database import Website, WebPage, TextChunk, ChatMessage, IngestionTask
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class WebsiteRepository:
    """Repository for website operations."""

    @staticmethod
    def create(db: Session, url: str, title: Optional[str] = None) -> Website:
        """Create a new website record."""
        website = Website(
            url=url,
            title=title or url,
            status="pending",
            total_pages=0,
            total_chunks=0,
        )
        db.add(website)
        db.commit()
        db.refresh(website)
        return website

    @staticmethod
    def get_by_id(db: Session, website_id: str) -> Optional[Website]:
        """Get website by ID."""
        return db.query(Website).filter(Website.id == website_id).first()

    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Website]:
        """Get website by URL."""
        return db.query(Website).filter(Website.url == url).first()

    @staticmethod
    def get_all(db: Session) -> List[Website]:
        """Get all websites."""
        return db.query(Website).all()

    @staticmethod
    def update_status(db: Session, website_id: str, status: str) -> Website:
        """Update website status."""
        website = db.query(Website).filter(Website.id == website_id).first()
        if website:
            website.status = status
            if website.total_pages is None:
                website.total_pages = 0
            if website.total_chunks is None:
                website.total_chunks = 0
            website.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(website)
        return website

    @staticmethod
    def update_crawl_metadata(
        db: Session, website_id: str, total_pages: int, total_chunks: int
    ) -> Website:
        """Update crawl metadata."""
        website = db.query(Website).filter(Website.id == website_id).first()
        if website:
            website.total_pages = total_pages
            website.total_chunks = total_chunks
            website.last_crawled = datetime.utcnow()
            website.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(website)
        return website

    @staticmethod
    def delete(db: Session, website_id: str) -> bool:
        """Delete website and cascade relationships."""
        website = db.query(Website).filter(Website.id == website_id).first()
        if website:
            db.delete(website)
            db.commit()
            return True
        return False


class WebPageRepository:
    """Repository for web page operations."""

    @staticmethod
    def create(
        db: Session,
        website_id: str,
        url: str,
        title: Optional[str] = None,
        content_raw: Optional[str] = None,
    ) -> WebPage:
        """Create a new web page record."""
        page = WebPage(
            website_id=website_id,
            url=url,
            title=title,
            content_raw=content_raw,
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        return page

    @staticmethod
    def get_by_id(db: Session, page_id: str) -> Optional[WebPage]:
        """Get web page by ID."""
        return db.query(WebPage).filter(WebPage.id == page_id).first()

    @staticmethod
    def get_by_website(db: Session, website_id: str) -> List[WebPage]:
        """Get all pages for a website."""
        return db.query(WebPage).filter(WebPage.website_id == website_id).all()

    @staticmethod
    def update(
        db: Session,
        page_id: str,
        content_cleaned: str,
        word_count: int,
        status: str = "success",
    ) -> WebPage:
        """Update page content and metadata."""
        page = db.query(WebPage).filter(WebPage.id == page_id).first()
        if page:
            page.content_cleaned = content_cleaned
            page.word_count = word_count
            page.status = status
            db.commit()
            db.refresh(page)
        return page


class TextChunkRepository:
    """Repository for text chunk operations."""

    @staticmethod
    def bulk_create(db: Session, chunks: List[dict]) -> List[TextChunk]:
        """Create multiple chunks at once."""
        chunk_objects = [TextChunk(**chunk) for chunk in chunks]
        db.add_all(chunk_objects)
        db.commit()
        return chunk_objects

    @staticmethod
    def get_by_website(db: Session, website_id: str) -> List[TextChunk]:
        """Get all chunks for a website."""
        return db.query(TextChunk).filter(TextChunk.website_id == website_id).all()

    @staticmethod
    def get_by_page(db: Session, page_id: str) -> List[TextChunk]:
        """Get all chunks for a page."""
        return db.query(TextChunk).filter(TextChunk.page_id == page_id).all()

    @staticmethod
    def mark_embedded(db: Session, chunk_ids: List[str]) -> None:
        """Mark chunks as having embeddings."""
        db.query(TextChunk).filter(TextChunk.id.in_(chunk_ids)).update(
            {TextChunk.embedding_generated: True}
        )
        db.commit()

    @staticmethod
    def get_uneeded_embeddings(db: Session, website_id: str) -> List[TextChunk]:
        """Get chunks that need embeddings."""
        return db.query(TextChunk).filter(
            TextChunk.website_id == website_id,
            TextChunk.embedding_generated == False,
        ).all()


class ChatMessageRepository:
    """Repository for chat message operations."""

    @staticmethod
    def create(
        db: Session,
        session_id: str,
        user_message: str,
        assistant_response: str,
        retrieved_chunks: int = 0,
        response_time: float = 0,
        model_used: str = "unknown",
        tokens_used: int = 0,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id,
            user_message=user_message,
            assistant_response=assistant_response,
            retrieved_chunks=retrieved_chunks,
            response_time=response_time,
            model_used=model_used,
            tokens_used=tokens_used,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_by_session(db: Session, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat history for a session."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )


class IngestionTaskRepository:
    """Repository for ingestion task tracking."""

    @staticmethod
    def create(
        db: Session, website_id: str, task_type: str
    ) -> IngestionTask:
        """Create a new ingestion task."""
        task = IngestionTask(website_id=website_id, task_type=task_type)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_active_tasks(db: Session, website_id: str) -> List[IngestionTask]:
        """Get active tasks for a website."""
        return db.query(IngestionTask).filter(
            IngestionTask.website_id == website_id,
            IngestionTask.status.in_(["pending", "running"]),
        ).all()

    @staticmethod
    def update_progress(
        db: Session, task_id: str, processed: int, total: int, status: str
    ) -> IngestionTask:
        """Update task progress."""
        task = db.query(IngestionTask).filter(IngestionTask.id == task_id).first()
        if task:
            task.processed_items = processed
            task.total_items = total
            task.status = status
            if status == "running" and not task.started_at:
                task.started_at = datetime.utcnow()
            elif status == "completed":
                task.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
        return task
