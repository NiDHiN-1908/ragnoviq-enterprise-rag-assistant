# RAGNoviq Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Chat Interface │ Dashboard │ Source Browser │ Dark Mode │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                      │
│                    TailwindCSS Styling                            │
│                    Zustand State Management                       │
└─────────────────────────────────────────────────────────────────┘
                             ↓
                      Axios HTTP Client
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Routes Layer                      │   │
│  │  ┌──────────────┬──────────────┬──────────────────────┐ │   │
│  │  │  Ingestion   │    Chat      │  System & Health     │ │   │
│  │  └──────────────┴──────────────┴──────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Services Layer                          │   │
│  │  ┌─────────────────────────────────────────────────────┐│   │
│  │  │ Crawler    Chunker    Embeddings  RAG Retriever    ││   │
│  │  │                                                     ││   │
│  │  │  LLM Generator  Ingestion Pipeline   Content Parser││   │
│  │  └─────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │             Data Access Layer (Repositories)            │   │
│  │  Website │ WebPage │ TextChunk │ ChatMessage │ Ingestion│   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         ↓                                    ↓
┌────────────────────────────    ────────────────────────────┐
│      Vector Database (FAISS)          Relational DB      │
│                                       (SQLite)             │
│  • Embeddings Index          • Websites metadata         │
│  • Similarity Search         • Pages & chunks            │
│  • Metadata Filtering        • Chat history             │
│  • Fast retrieval (ms)       • Ingestion tracking       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Indexing Pipeline
```
1. Website URL Submission
         ↓
2. Recursive Web Crawling
   - Depth-limited crawl
   - Internal link discovery
   - Content extraction
         ↓
3. Content Parsing
   - HTML to text conversion
   - Boilerplate removal
   - Metadata extraction
         ↓
4. Semantic Chunking
   - Paragraph-based splitting
   - Sentence-level refinement
   - Overlap handling
         ↓
5. Embedding Generation
   - sentence-transformers
   - Batch processing
   - Vector normalization
         ↓
6. Vector Indexing
   - FAISS index update
   - Metadata storage
   - SQLite persistence
         ↓
7. Status Updated to UI
   - Progress notifications
   - Completion signals
```

### Query Pipeline
```
1. User Question
         ↓
2. Query Embedding
   - sentence-transformers
   - Semantic representation
         ↓
3. Vector Similarity Search
   - FAISS indexing
   - Top-K retrieval
   - Similarity scoring
         ↓
4. Context Retrieval
   - Filter by website (optional)
   - Sort by relevance
   - Format with metadata
         ↓
5. LLM Prompt Building
   - System instructions
   - Retrieved context
   - Conversation history
         ↓
6. Response Generation
   - Groq or Gemini API
   - Token counting
   - Response time tracking
         ↓
7. Source Citation
   - Link retrieved chunks
   - Calculate relevance
   - Format for display
         ↓
8. Response to User
   - Stream/return answer
   - Show sources
   - Store in history
```

## Component Architecture

### Backend Services

#### Crawler Service
- **Purpose**: Recursive website crawling
- **Key Features**:
  - Depth-limited traversal
  - Domain boundary checking
  - URL deduplication
  - Retry logic with backoff
  - Session management with headers

#### Chunker Service
- **Purpose**: Semantic text chunking
- **Key Features**:
  - Paragraph-aware splitting
  - Sentence-level refinement
  - Minimum chunk size enforcement
  - Overlap handling
  - Metadata preservation

#### Embeddings Service
- **Purpose**: Generate semantic embeddings
- **Key Features**:
  - sentence-transformers integration
  - Batch processing
  - Empty text handling
  - Cosine similarity calculation
  - Vectorized operations

#### FAISS Vector DB
- **Purpose**: Fast similarity search
- **Key Features**:
  - Flat L2 index (scalable to IVF)
  - Metadata JSON storage
  - Persistence to disk
  - Website-based filtering
  - Similarity scoring

#### RAG Retriever
- **Purpose**: Context retrieval
- **Key Features**:
  - Query embedding
  - Top-K similarity search
  - Threshold filtering
  - Website filtering
  - Result formatting

#### LLM Generator
- **Purpose**: Response generation
- **Key Features**:
  - Multi-provider support (Groq/Gemini)
  - Prompt engineering
  - Grounding validation
  - Token counting
  - Context window management

#### Ingestion Pipeline
- **Purpose**: Orchestrate full indexing
- **Key Features**:
  - Service coordination
  - Error handling
  - Progress tracking
  - DB transaction management

### Frontend Components

#### Layout
- Navigation sidebar
- Dark mode toggle
- Responsive mobile menu

#### Chat Page
- Message display
- Input form with send button
- Source citations
- Loading states
- Error handling

#### Dashboard
- Website list
- Add website form
- Statistics cards
- Delete functionality
- Progress tracking

#### Sources Page
- Indexed sources browser
- URL linking
- Statistics display
- Refresh capability

## Database Schema

### Websites Table
```
id (UUID)
url (String, unique)
title (String)
description (Text)
status (String: pending, indexing, indexed, failed)
total_pages (Integer)
total_chunks (Integer)
last_crawled (DateTime)
created_at (DateTime)
updated_at (DateTime)
```

### WebPages Table
```
id (UUID)
website_id (FK)
url (String)
title (String)
content_raw (Text)
content_cleaned (Text)
word_count (Integer)
status (String)
error_message (Text)
crawled_at (DateTime)
```

### TextChunks Table
```
id (UUID)
website_id (FK)
page_id (FK)
content (Text)
chunk_index (Integer)
start_char (Integer)
end_char (Integer)
embedding_id (String)
embedding_generated (Boolean)
created_at (DateTime)
```

### ChatMessages Table
```
id (UUID)
session_id (String)
user_message (Text)
assistant_response (Text)
retrieved_chunks (Integer)
response_time (Float)
model_used (String)
tokens_used (Integer)
created_at (DateTime)
```

## API Contract

### Request/Response Examples

#### POST /api/v1/ingest/website
```json
Request:
{
  "url": "https://example.com",
  "title": "Example Website"
}

Response (202):
{
  "id": "uuid",
  "url": "https://example.com",
  "title": "Example Website",
  "status": "pending",
  "total_pages": 0,
  "total_chunks": 0,
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST /api/v1/chat/query
```json
Request:
{
  "question": "What is your product?",
  "session_id": "optional_session_id",
  "use_websites": ["website_id"]
}

Response:
{
  "answer": "Our product is...",
  "sources": [
    {
      "title": "About Us",
      "url": "https://example.com/about",
      "relevance": 0.95
    }
  ],
  "session_id": "session_uuid",
  "model_used": "mixtral-8x7b-32768",
  "tokens_used": 256,
  "response_time": 2.34
}
```

## Performance Characteristics

### Indexing
- **Small site** (< 100 pages): 2-5 minutes
- **Medium site** (100-1000 pages): 15-30 minutes
- **Large site** (1000+ pages): 1-2 hours

### Query Response
- **Retrieval**: 100-500ms (FAISS similarity search)
- **LLM Generation**: 1-3 seconds (network dependent)
- **Total**: 2-5 seconds typical response time

### Storage
- **Per page**: ~50KB average
- **Per chunk**: ~2KB average
- **Embeddings**: ~2MB per 1000 documents

## Scalability Considerations

### Horizontal Scaling
- Stateless FastAPI backend (scale horizontally)
- Vector DB can be replicated
- Frontend is static (CDN-ready)

### Vertical Scaling
- Batch embedding processing
- Connection pooling
- Caching mechanisms
- Async processing

### Optimization Opportunities
- Switch to IVF index for large datasets
- Implement Redis caching
- Use Elasticsearch for document search
- Add streaming responses
- Implement pagination
