"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


# =====================
# Website Schemas
# =====================

class WebsiteCreate(BaseModel):
    """Schema for creating a new website indexing task."""
    url: str = Field(..., description="Website URL to crawl and index")
    title: Optional[str] = Field(None, description="Custom title for the website")

    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        if not v.startswith("http://") and not v.startswith("https://"):
            v = "https://" + v
        return v.rstrip("/")


class WebsiteResponse(BaseModel):
    """Schema for website response."""
    id: str
    url: str
    title: Optional[str] = None
    status: str = "pending"
    total_pages: int = 0
    total_chunks: int = 0
    last_crawled: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class WebsiteDetail(WebsiteResponse):
    """Detailed website information."""
    description: Optional[str]
    updated_at: datetime


# =====================
# Chat Schemas
# =====================

class ChatMessage(BaseModel):
    """Schema for chat messages."""
    question: str = Field(..., description="User question")
    session_id: Optional[str] = Field(None, description="Chat session ID for history")
    use_websites: Optional[List[str]] = Field(
        None, description="List of website IDs to search in"
    )


class ChatResponse(BaseModel):
    """Schema for chat response."""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[dict] = Field(default=[], description="Source references")
    session_id: str = Field(..., description="Chat session ID")
    model_used: str = Field(..., description="LLM model used")
    tokens_used: int = Field(0, description="Tokens used for this request")
    response_time: float = Field(..., description="Response time in seconds")


class ChatHistory(BaseModel):
    """Schema for chat history."""
    session_id: str
    messages: List[dict]
    created_at: datetime
    total_messages: int


# =====================
# Ingestion Status Schemas
# =====================

class IngestionStatus(BaseModel):
    """Schema for ingestion progress status."""
    website_id: str
    website_url: str
    status: str  # pending, indexing, indexed, failed
    total_pages: int = 0
    processed_pages: int = 0
    current_task: Optional[str] = None
    progress_percentage: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class SystemStatus(BaseModel):
    """Schema for overall system status."""
    status: str  # healthy, degraded, error
    total_websites: int
    total_pages_indexed: int
    total_chunks: int
    vector_db_size: int
    uptime_seconds: int
    active_tasks: int
    cache_hits: int
    cache_misses: int


# =====================
# Source Schemas
# =====================

class SourceReference(BaseModel):
    """Schema for source citation."""
    website_id: str
    website_url: str
    page_url: str
    page_title: Optional[str]
    chunk_index: int
    excerpt: str
    relevance_score: float


class SourceListResponse(BaseModel):
    """Schema for list of indexed sources."""
    total_websites: int
    websites: List[WebsiteResponse]


# =====================
# Admin Dashboard Schemas
# =====================

class DashboardMetrics(BaseModel):
    """Schema for admin dashboard metrics."""
    total_websites: int
    total_pages_crawled: int
    total_chunks_created: int
    average_chunk_size: float
    embeddings_generated: int
    total_queries: int
    average_query_latency: float
    token_usage_today: int
    failed_ingestions: int
    storage_used_mb: float


class QueryMetric(BaseModel):
    """Schema for query metrics."""
    timestamp: datetime
    query: str
    response_time: float
    tokens_used: int
    model: str
    success: bool


# =====================
# Error Schemas
# =====================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorDetail(BaseModel):
    """Schema for validation error details."""
    field: str
    message: str
    value: Optional[str] = None
