"""
Ingestion API routes.
Handles website URL submission and indexing management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.models import WebsiteCreate, WebsiteResponse, IngestionStatus
from app.services.ingestion import IngestionPipeline
from app.db.database import get_db
from app.db.repositories import WebsiteRepository
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])

pipeline = IngestionPipeline()


@router.post("/website", response_model=WebsiteResponse, status_code=202)
async def ingest_website(
    website: WebsiteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit a website for indexing.
    
    Returns:
        Website record with status 'pending' or 'indexing'
    """
    try:
        # Check if URL already exists
        existing = WebsiteRepository.get_by_url(db, str(website.url))
        if existing:
            if existing.status == "indexed":
                raise HTTPException(
                    status_code=409,
                    detail="Website already indexed. Use PUT to re-index.",
                )
            return existing

        # Add to background tasks
        background_tasks.add_task(
            pipeline.ingest_website, str(website.url), website.title
        )

        # Create and return website record
        new_website = WebsiteRepository.create(
            db, url=str(website.url), title=website.title
        )

        logger.info(f"Submitted website for indexing: {new_website.id}")

        return new_website

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting website: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit website")


@router.get("/status/{website_id}", response_model=IngestionStatus)
async def get_ingestion_status(website_id: str, db: Session = Depends(get_db)):
    """Get ingestion status for a website."""
    try:
        website = WebsiteRepository.get_by_id(db, website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")

        # Calculate progress
        progress = 0
        if website.total_pages > 0:
            progress = int((website.total_chunks / (website.total_pages * 10)) * 100)
            progress = min(progress, 99) if website.status == "indexing" else 100

        return IngestionStatus(
            website_id=website.id,
            website_url=website.url,
            status=website.status,
            total_pages=website.total_pages,
            processed_pages=website.total_pages,
            current_task="chunking" if website.status == "indexing" else None,
            progress_percentage=progress,
            error_message=None,
            started_at=website.created_at,
            estimated_completion=website.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.delete("/website/{website_id}")
async def delete_website(website_id: str, db: Session = Depends(get_db)):
    """Delete a website and all its indexed data."""
    try:
        website = WebsiteRepository.get_by_id(db, website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")

        pipeline.delete_website(website_id)

        logger.info(f"Deleted website: {website_id}")

        return {"message": "Website deleted successfully", "website_id": website_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting website: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete website")


@router.get("/websites")
async def list_websites(db: Session = Depends(get_db)):
    """List all indexed websites."""
    try:
        websites = WebsiteRepository.get_all(db)
        return {
            "total": len(websites),
            "websites": [
                {
                    "id": w.id,
                    "url": w.url,
                    "title": w.title,
                    "status": w.status,
                    "pages": w.total_pages,
                    "chunks": w.total_chunks,
                    "created_at": w.created_at,
                }
                for w in websites
            ],
        }

    except Exception as e:
        logger.error(f"Error listing websites: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list websites")
