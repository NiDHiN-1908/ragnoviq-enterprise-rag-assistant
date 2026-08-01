"""
Comprehensive Test Suite for RAGNoviq Backend.
Tests chunking, embeddings, FAISS vector DB, hybrid retrieval, LLM prompt generation, database repositories, and API routes.
"""

import os
import pytest
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import get_settings
from app.services.chunker import TextChunker
from app.services.embeddings import EmbeddingGenerator
from app.vector_db.faiss_db import FAISSVectorDB
from app.services.retriever import RAGRetriever
from app.services.llm_generator import LLMGenerator
from app.db.database import SessionLocal, init_db, drop_db
from app.db.repositories import (
    WebsiteRepository,
    WebPageRepository,
    TextChunkRepository,
    ChatMessageRepository,
)
from app.models.database import ChatMessage as ChatMessageModel

settings = get_settings()
client = TestClient(app)


# Setup fixture for clean test database
@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    yield
    # Cleanup test artifacts if needed


# ==========================================
# 1. Text Chunker Service Tests
# ==========================================
def test_text_chunker_basic():
    chunker = TextChunker(chunk_size=200, chunk_overlap=30)
    sample_text = (
        "RAGNoviq is an enterprise AI assistant platform. "
        "It uses hybrid retrieval and FAISS vector databases to index websites. "
        "The system parses HTML, generates semantic embeddings, and powers LLMs. "
        "This is an extra sentence to verify chunking and overlap functionality."
    )
    chunks = chunker.chunk_text(sample_text, metadata={"page_id": "test_page_1"})
    
    assert len(chunks) > 0
    assert "content" in chunks[0]
    assert "chunk_index" in chunks[0]
    assert chunks[0]["metadata"]["page_id"] == "test_page_1"


def test_text_chunker_empty():
    chunker = TextChunker()
    chunks = chunker.chunk_text("", metadata={})
    assert len(chunks) == 0


# ==========================================
# 2. Embedding Generator Tests
# ==========================================
def test_embedding_generator_dimensions():
    embedder = EmbeddingGenerator()
    dim = embedder.get_embedding_dimension()
    assert dim == 384

    vec = embedder.generate_embedding("Hello world RAG chatbot")
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (384,)


def test_embedding_generator_batch():
    embedder = EmbeddingGenerator()
    texts = ["First document text", "Second document text", "Third document text"]
    vecs = embedder.generate_embeddings_batch(texts)
    assert len(vecs) == 3
    assert vecs[0].shape == (384,)


def test_embedding_similarity():
    embedder = EmbeddingGenerator()
    vec1 = embedder.generate_embedding("Artificial Intelligence and Machine Learning")
    vec2 = embedder.generate_embedding("AI and Deep Learning algorithms")
    vec3 = embedder.generate_embedding("Baking chocolate cake recipes")

    sim12 = embedder.similarity(vec1, vec2)
    sim13 = embedder.similarity(vec1, vec3)

    assert sim12 > sim13


# ==========================================
# 3. FAISS Vector DB & Index Rebuilding Tests
# ==========================================
def test_faiss_add_search_delete(tmp_path):
    test_db_dir = str(tmp_path / "test_vector_db")
    vdb = FAISSVectorDB(vector_db_path=test_db_dir, dimension=384)

    # Generate dummy vectors
    vecs_site_a = np.random.rand(5, 384).astype(np.float32)
    meta_site_a = [{"content": f"Site A Chunk {i}", "chunk_index": i} for i in range(5)]

    vecs_site_b = np.random.rand(3, 384).astype(np.float32)
    meta_site_b = [{"content": f"Site B Chunk {i}", "chunk_index": i} for i in range(3)]

    vdb.add_vectors(vecs_site_a, meta_site_a, website_id="site_a")
    vdb.add_vectors(vecs_site_b, meta_site_b, website_id="site_b")

    assert vdb.get_stats()["total_vectors"] == 8

    # Search website A
    results = vdb.search(vecs_site_a[0], top_k=2, website_id="site_a")
    assert len(results) > 0
    assert results[0][2]["website_id"] == "site_a"

    # Delete website A vectors
    deleted_count = vdb.delete_vectors("site_a")
    assert deleted_count == 5

    # Verify site_b vectors REMAIN in index (Bugfix verification!)
    assert vdb.get_stats()["total_vectors"] == 3
    results_after = vdb.search(vecs_site_b[0], top_k=2, website_id="site_b")
    assert len(results_after) > 0
    assert results_after[0][2]["website_id"] == "site_b"


# ==========================================
# 4. RAG Retriever Hybrid Search Tests
# ==========================================
def test_rag_retriever_hybrid_search(tmp_path):
    test_db_dir = str(tmp_path / "test_retriever_db")
    retriever = RAGRetriever()
    retriever.vector_db = FAISSVectorDB(vector_db_path=test_db_dir, dimension=retriever.embedding_generator.embedding_dim)

    chunks = [
        {"content": "Python is a high-level programming language used in AI and data science.", "page_title": "Python Guide", "page_url": "https://python.org"},
        {"content": "FastAPI is a modern web framework for building APIs with Python.", "page_title": "FastAPI Docs", "page_url": "https://fastapi.tiangolo.com"},
        {"content": "SQLite is a lightweight C library that provides a disk-based relational database.", "page_title": "SQLite Docs", "page_url": "https://sqlite.org"},
    ]

    retriever.add_documents(chunks, website_id="dev_docs")

    # Perform hybrid search for "FastAPI web framework"
    results = retriever.retrieve_context("FastAPI web framework", website_id="dev_docs", top_k=2)
    assert len(results) > 0
    assert "FastAPI" in results[0]["content"]


# ==========================================
# 5. LLM Generator Prompt & Fallback Tests
# ==========================================
def test_llm_generator_prompt_untruncated():
    gen = LLMGenerator()
    long_content = "Word " * 300  # ~1500 chars
    context = [{
        "page_title": "Long Document",
        "page_url": "https://example.com/long",
        "similarity_score": 0.92,
        "content": long_content
    }]

    prompt = gen._build_prompt("What is this document about?", context)
    assert "Word Word" in prompt
    assert "Full Content:" in prompt


def test_llm_generator_fallback():
    gen = LLMGenerator()
    response, tokens, duration = gen.generate_response(
        query="What is the key topic?",
        context=[{"page_title": "Sample", "page_url": "https://sample.com", "similarity_score": 0.85, "content": "Sample content about RAG AI chatbots."}]
    )
    assert len(response) > 0
    assert duration >= 0.0


# ==========================================
# 6. Database Repositories Tests
# ==========================================
def test_database_repositories():
    db = SessionLocal()
    try:
        # Create website
        site = WebsiteRepository.create(db, url="https://test-site.org", title="Test Site")
        assert site.id is not None
        assert site.status == "pending"

        # Update status
        updated = WebsiteRepository.update_status(db, site.id, "indexed")
        assert updated.status == "indexed"

        # Create chat message
        msg = ChatMessageRepository.create(
            db,
            session_id="test_sess_100",
            user_message="Hello AI",
            assistant_response="Hello User",
            retrieved_chunks=2,
            response_time=0.45,
            model_used="test-model",
            tokens_used=50,
        )
        assert msg.id is not None

        # Fetch history
        history = ChatMessageRepository.get_by_session(db, "test_sess_100")
        assert len(history) == 1
        assert history[0].user_message == "Hello AI"
    finally:
        db.close()


# ==========================================
# 7. FastAPI Endpoints Integration Tests
# ==========================================
def test_health_check_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_system_status_endpoint():
    res = client.get("/api/v1/status")
    assert res.status_code == 200
    data = res.json()
    assert "websites" in data
    assert "system" in data


def test_sources_endpoint():
    res = client.get("/api/v1/sources")
    assert res.status_code == 200
    data = res.json()
    assert "sources" in data


def test_chat_query_and_clear_session_endpoint():
    # Test chat query endpoint
    res = client.post("/api/v1/chat/query", json={
        "question": "What is RAGNoviq?",
        "session_id": "test_sess_api_99"
    })
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert data["session_id"] == "test_sess_api_99"

    # Test clear session endpoint
    del_res = client.delete("/api/v1/chat/session/test_sess_api_99")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["deleted_count"] >= 1


def test_ingest_website_normalization_and_reindex():
    # Test website submission with bare domain (missing https://)
    res = client.post("/api/v1/ingest/website", json={
        "url": "example.com"
    })
    assert res.status_code == 202
    data = res.json()
    assert data["url"] == "https://example.com"

    # Test re-submitting same website
    re_res = client.post("/api/v1/ingest/website", json={
        "url": "https://example.com"
    })
    assert re_res.status_code == 202
    re_data = re_res.json()
    assert re_data["id"] == data["id"]

