"""
Database models for RAGNoviq application.
Uses SQLAlchemy ORM for data persistence.
"""

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Website(Base):
    """Model for indexed websites."""
    __tablename__ = "websites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, indexing, indexed, failed
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    last_crawled = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pages = relationship("WebPage", back_populates="website", cascade="all, delete-orphan")
    chunks = relationship("TextChunk", back_populates="website", cascade="all, delete-orphan")


class WebPage(Base):
    """Model for crawled web pages."""
    __tablename__ = "web_pages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    website_id = Column(String, ForeignKey("websites.id"), nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    content_raw = Column(Text, nullable=True)
    content_cleaned = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    status = Column(String, default="success")  # success, failed
    error_message = Column(Text, nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    website = relationship("Website", back_populates="pages")
    chunks = relationship("TextChunk", back_populates="page", cascade="all, delete-orphan")


class TextChunk(Base):
    """Model for text chunks created from web pages."""
    __tablename__ = "text_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    website_id = Column(String, ForeignKey("websites.id"), nullable=False, index=True)
    page_id = Column(String, ForeignKey("web_pages.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    embedding_id = Column(String, nullable=True, index=True)  # Reference to vector DB
    embedding_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    website = relationship("Website", back_populates="chunks")
    page = relationship("WebPage", back_populates="chunks")


class ChatMessage(Base):
    """Model for chat messages and conversation history."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    retrieved_chunks = Column(Integer, default=0)
    response_time = Column(Float, nullable=True)  # in seconds
    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class APIKey(Base):
    """Model for API key management."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class IngestionTask(Base):
    """Model for tracking ingestion tasks."""
    __tablename__ = "ingestion_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    website_id = Column(String, ForeignKey("websites.id"), nullable=False, index=True)
    task_type = Column(String, nullable=False)  # crawl, parse, chunk, embed
    status = Column(String, default="pending")  # pending, running, completed, failed
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """Model for system logging and monitoring."""
    __tablename__ = "system_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String, nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    module = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    log_metadata = Column(Text, nullable=True)  # JSON string
