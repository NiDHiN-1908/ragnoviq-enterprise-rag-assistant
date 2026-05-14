# Project Artifacts

All project files and artifacts are in this directory.

## Root Files

- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `README.md` - Main project documentation
- `ARCHITECTURE.md` - System architecture documentation
- `DEPLOYMENT.md` - Deployment guide
- `ROADMAP.md` - Implementation roadmap
- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile.backend` - Backend Docker image
- `Dockerfile.frontend` - Frontend Docker image

## Backend Directory

```
backend/
├── app/
│   ├── main.py               # FastAPI application entry point
│   ├── api/                  # API routes
│   │   ├── ingestion.py      # Website ingestion endpoints
│   │   ├── chat.py           # Chat endpoints
│   │   └── system.py         # System health endpoints
│   ├── services/             # Business logic
│   │   ├── crawler.py        # Web crawling
│   │   ├── chunker.py        # Text chunking
│   │   ├── embeddings.py     # Embedding generation
│   │   ├── retriever.py      # RAG retrieval
│   │   ├── llm_generator.py  # LLM response generation
│   │   └── ingestion.py      # Pipeline orchestration
│   ├── models/               # SQLAlchemy ORM models
│   │   └── database.py       # Database models
│   ├── schemas/              # Pydantic request/response schemas
│   │   └── models.py         # Request/response models
│   ├── db/                   # Database layer
│   │   ├── database.py       # Connection management
│   │   └── repositories.py   # Data access layer
│   ├── vector_db/            # Vector database
│   │   └── faiss_db.py       # FAISS implementation
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration management
│   │   └── logging.py        # Logging setup
│   └── utils/                # Utilities
│       ├── helpers.py        # Helper functions
│       └── parser.py         # Content parsing
└── requirements.txt          # Python dependencies
```

## Frontend Directory

```
frontend/
├── src/
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # React entry point
│   ├── store.js             # Zustand state management
│   ├── components/          # Reusable components
│   │   ├── Layout.jsx       # Main layout with sidebar
│   │   ├── ChatMessage.jsx  # Chat message display
│   │   ├── SourceCard.jsx   # Source reference card
│   │   ├── WebsiteCard.jsx  # Website card component
│   │   └── WebsiteForm.jsx  # Website form component
│   ├── pages/               # Page components
│   │   ├── ChatPage.jsx     # Chat interface
│   │   ├── DashboardPage.jsx # Admin dashboard
│   │   └── SourcesPage.jsx  # Sources browser
│   ├── services/            # API client
│   │   └── api.js           # Axios configuration
│   └── styles/              # Stylesheets
│       └── globals.css      # Global styles
├── index.html               # HTML entry point
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # TailwindCSS configuration
├── postcss.config.js       # PostCSS configuration
└── package.json            # Node dependencies
```

## File Summary

### Core Backend Files (6)
1. `app/main.py` - 100 lines
2. `app/db/database.py` - 50 lines
3. `app/db/repositories.py` - 180 lines
4. `app/models/database.py` - 150 lines
5. `app/schemas/models.py` - 180 lines
6. `app/core/config.py` - 100 lines

### Services (6)
1. `app/services/crawler.py` - 180 lines
2. `app/services/chunker.py` - 150 lines
3. `app/services/embeddings.py` - 140 lines
4. `app/services/retriever.py` - 100 lines
5. `app/services/llm_generator.py` - 200 lines
6. `app/services/ingestion.py` - 200 lines

### API Routes (3)
1. `app/api/ingestion.py` - 100 lines
2. `app/api/chat.py` - 140 lines
3. `app/api/system.py` - 120 lines

### Vector Database (1)
1. `app/vector_db/faiss_db.py` - 180 lines

### Utils (2)
1. `app/utils/helpers.py` - 80 lines
2. `app/utils/parser.py` - 90 lines

### Frontend Components (8)
1. `App.jsx` - 20 lines
2. `Layout.jsx` - 120 lines
3. `ChatMessage.jsx` - 25 lines
4. `SourceCard.jsx` - 25 lines
5. `WebsiteCard.jsx` - 60 lines
6. `WebsiteForm.jsx` - 60 lines
7. `api.js` - 20 lines
8. `store.js` - 15 lines

### Frontend Pages (3)
1. `ChatPage.jsx` - 150 lines
2. `DashboardPage.jsx` - 140 lines
3. `SourcesPage.jsx` - 100 lines

### Documentation (4)
1. `README.md` - 400 lines
2. `ARCHITECTURE.md` - 300 lines
3. `DEPLOYMENT.md` - 350 lines
4. `ROADMAP.md` - 300 lines

### Configuration Files (6)
1. `.env.example` - 50 lines
2. `requirements.txt` - 40 lines
3. `package.json` - 30 lines
4. `vite.config.js` - 20 lines
5. `tailwind.config.js` - 15 lines
6. `postcss.config.js` - 8 lines

### Docker Files (3)
1. `docker-compose.yml` - 60 lines
2. `Dockerfile.backend` - 30 lines
3. `Dockerfile.frontend` - 25 lines

**Total: ~3,500+ lines of production-quality code and documentation**
