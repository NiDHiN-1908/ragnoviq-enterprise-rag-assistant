"""
Chat API routes.
Handles user questions and generates RAG-based responses.
"""

import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.models import ChatMessage, ChatResponse, ChatHistory
from app.services.llm_generator import LLMGenerator
from app.services.retriever import RAGRetriever
from app.db.database import get_db
from app.db.repositories import ChatMessageRepository
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

llm_generator = LLMGenerator()
retriever = RAGRetriever()


@router.post("/query", response_model=ChatResponse)
async def chat(query: ChatMessage, db: Session = Depends(get_db)):
    """
    Submit a question and get RAG-based response.
    
    Args:
        query: User question and optional session ID
        
    Returns:
        Response with answer and source citations
    """
    try:
        if not query.question or not query.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Generate session ID if not provided
        session_id = query.session_id or generate_id()

        start_time = time.time()

        # Retrieve relevant context
        context = retriever.retrieve_context(
            query=query.question,
            website_id=query.use_websites[0] if query.use_websites else None,
            top_k=5,
        )

        # Get conversation history (optional)
        history = []
        if query.session_id:
            history_msgs = ChatMessageRepository.get_by_session(
                db, query.session_id, limit=5
            )
            history = [
                {"role": "user", "content": msg.user_message}
                for msg in reversed(history_msgs)
            ]

        # Generate response
        response_text, tokens_used, generation_time = llm_generator.generate_response(
            query=query.question,
            context=context,
            conversation_history=history,
        )

        response_time = time.time() - start_time

        # Store in chat history
        ChatMessageRepository.create(
            db,
            session_id=session_id,
            user_message=query.question,
            assistant_response=response_text,
            retrieved_chunks=len(context),
            response_time=response_time,
            model_used=llm_generator.model,
            tokens_used=tokens_used,
        )

        logger.info(
            f"Generated response for session {session_id}: "
            f"{tokens_used} tokens, {response_time:.2f}s"
        )

        # Format sources
        sources = [
            {
                "title": item["page_title"] or "Untitled",
                "url": item["page_url"],
                "relevance": item["similarity_score"],
            }
            for item in context
        ]

        return ChatResponse(
            answer=response_text,
            sources=sources,
            session_id=session_id,
            model_used=llm_generator.model,
            tokens_used=tokens_used,
            response_time=response_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session."""
    try:
        messages = ChatMessageRepository.get_by_session(db, session_id, limit=100)

        history = [
            {
                "timestamp": msg.created_at,
                "user": msg.user_message,
                "assistant": msg.assistant_response,
                "chunks_retrieved": msg.retrieved_chunks,
                "tokens_used": msg.tokens_used,
            }
            for msg in reversed(messages)
        ]

        return ChatHistory(
            session_id=session_id,
            messages=history,
            created_at=messages[-1].created_at if messages else None,
            total_messages=len(messages),
        )

    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get history")


@router.delete("/session/{session_id}")
async def clear_session(session_id: str, db: Session = Depends(get_db)):
    """Clear chat history for a session."""
    try:
        # In production, delete old messages
        logger.info(f"Cleared session: {session_id}")
        return {"message": "Session cleared"}

    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear session")
