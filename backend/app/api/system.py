"""
System status and health check routes.
"""

import logging
import psutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import WebsiteRepository, ChatMessageRepository
from app.services.retriever import RAGRetriever
from app.services.llm_generator import LLMGenerator
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["system"])

retriever = RAGRetriever()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}, 500


@router.get("/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status and metrics."""
    try:
        websites = WebsiteRepository.get_all(db)
        
        total_pages = sum(w.total_pages for w in websites)
        total_chunks = sum(w.total_chunks for w in websites)
        
        retriever_stats = retriever.get_stats()
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "websites": {
                "total_indexed": len(websites),
                "status_breakdown": {
                    "indexed": len([w for w in websites if w.status == "indexed"]),
                    "indexing": len([w for w in websites if w.status == "indexing"]),
                    "failed": len([w for w in websites if w.status == "failed"]),
                },
            },
            "indexing": {
                "total_pages_crawled": total_pages,
                "total_chunks_created": total_chunks,
                "total_vectors": retriever_stats.get("total_vectors", 0),
                "vector_db_size_mb": retriever_stats.get("index_file_size_mb", 0),
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
            },
        }

    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


@router.get("/sources")
async def get_indexed_sources(db: Session = Depends(get_db)):
    """Get list of all indexed sources."""
    try:
        websites = WebsiteRepository.get_all(db)
        
        sources = []
        for website in websites:
            if website.status == "indexed":
                sources.append({
                    "id": website.id,
                    "url": website.url,
                    "title": website.title or website.url,
                    "pages_indexed": website.total_pages,
                    "chunks_created": website.total_chunks,
                    "indexed_at": website.last_crawled,
                })

        return {
            "total_sources": len(sources),
            "sources": sources,
        }

    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        return {"total_sources": 0, "sources": []}


@router.get("/models")
async def get_model_info():
    """Get information about models in use."""
    try:
        llm_gen = LLMGenerator()
        
        return {
            "llm": llm_gen.get_model_info(),
            "embeddings": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "dimension": retriever.embedding_generator.get_embedding_dimension(),
            },
            "vector_db": "FAISS",
        }

    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return {}
