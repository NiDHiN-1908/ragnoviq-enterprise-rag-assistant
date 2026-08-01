import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import SessionLocal
from app.models.database import Website, WebPage, TextChunk
from app.services.retriever import RAGRetriever

def inspect():
    db = SessionLocal()
    try:
        websites = db.query(Website).all()
        print(f"=== INDEXED WEBSITES ({len(websites)}) ===")
        for w in websites:
            print(f"ID: {w.id} | URL: {w.url} | Status: {w.status} | Pages: {w.total_pages} | Chunks: {w.total_chunks}")
        
        pages = db.query(WebPage).all()
        print(f"\n=== WEB PAGES IN DB ({len(pages)}) ===")
        for p in pages:
            print(f"ID: {p.id} | Title: {p.title} | URL: {p.url} | Content Length: {len(p.content_cleaned or '')} chars")
            if p.content_cleaned:
                print(f"   Snippet: {p.content_cleaned[:200]}...")

        chunks = db.query(TextChunk).all()
        print(f"\n=== TEXT CHUNKS IN DB ({len(chunks)}) ===")
        for c in chunks[:5]:
            print(f"Chunk Index {c.chunk_index}: {c.content[:150]}...")

        retriever = RAGRetriever()
        print(f"\n=== FAISS VECTOR STORE ===")
        print(f"Total Vectors in FAISS: {len(retriever.vector_db.metadata)}")
        if retriever.vector_db.metadata:
            print(f"Sample Metadata: {retriever.vector_db.metadata[0]}")

    finally:
        db.close()

if __name__ == "__main__":
    inspect()
