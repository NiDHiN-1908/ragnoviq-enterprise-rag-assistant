# RAGNoviq — Enterprise RAG AI Knowledge Assistant 🚀

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18-blue)
![Vite](https://img.shields.io/badge/Vite-5.0-purple)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3%2070B-orange)
![Deploy](https://img.shields.io/badge/Deployed-Vercel%20%2B%20Render-success)

> A production-grade Enterprise Retrieval-Augmented Generation (RAG) system for turning website contents into interactive AI knowledge assistants with hybrid vector retrieval, zero-hallucination grounding, and inline citations.

---

## 🌐 Live Production Demos

| Component | Host Platform | Production URL |
| :--- | :--- | :--- |
| **Frontend UI (React/Vite)** | Vercel | [ragnoviq-enterprise-rag-assistant-3.vercel.app](https://ragnoviq-enterprise-rag-assistant-3.vercel.app) |
| **Backend REST API (FastAPI)** | Render | [ragnoviq-enterprise-rag-assistant.onrender.com](https://ragnoviq-enterprise-rag-assistant.onrender.com) |
| **API Swagger Docs** | Render | [ragnoviq-enterprise-rag-assistant.onrender.com/docs](https://ragnoviq-enterprise-rag-assistant.onrender.com/docs) |

---

## ✨ Features & Capabilities

- 🤖 **Groq LLaMA 3.3 70B Engine**: Sub-second AI inference (`~0.45s`) for enterprise context synthesis.
- ⚡ **Hybrid Vector Retrieval**: FAISS dense embeddings (384-dim) combined with 30% lexical keyword score weighting.
- 🌐 **Deep Web Crawler**: Multi-depth recursive crawling with HTML parsing, link discovery, and full DOM text extraction.
- 🎨 **Glassmorphism Dark UI**: Vibrant glass panels, custom scrollbars, search filters, and active icon highlights.
- 📊 **Real-time Admin Analytics**: Live website metrics, chunk counts, page counts, and domain search filters.
- 📌 **Grounded Citations**: Inline `[Source N]` tags with relevance match percentage bars and external domain links.
- 🛡️ **Double Fallback Architecture**: Deterministic feature hash fallback for vector embeddings + direct SQLite `TextChunk` query safety net.
- 🚀 **1-Click Multi-platform Launchers**: Launchers for Windows, Linux, Docker, Render, and Vercel.

---

## 🏗️ Architecture Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: SQLite + SQLAlchemy ORM
- **Vector Engine**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`) with 384-dim feature vector hash fallback
- **LLM Provider**: Groq API (`llama-3.3-70b-versatile`)
- **Parser**: BeautifulSoup4

### Frontend
- **Framework**: React 18 + Vite 5
- **Styling**: Vanilla CSS + TailwindCSS Design Tokens + Glassmorphism
- **Icons**: Lucide React
- **State**: Zustand + Axios

---

## 📁 Project Structure

```
ragnoviq-enterprise-rag-assistant/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes (ingestion, chat, system)
│   │   ├── services/         # Core business logic (crawler, chunker, RAG, LLM)
│   │   ├── models/           # SQLAlchemy database schemas
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── db/               # Database connection and repositories
│   │   ├── vector_db/        # FAISS vector database
│   │   └── main.py           # FastAPI application entrypoint
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components (Layout, Cards, Forms)
│   │   ├── pages/            # Page components (Dashboard, Chat, Sources)
│   │   ├── services/         # Axios API client
│   │   └── styles/           # CSS and glassmorphic utilities
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── run_backend.py            # Zero-configuration python backend entrypoint
├── start.py                  # Concurrent cross-platform python launcher
├── run.bat                   # 1-click Windows batch launcher
├── Dockerfile.backend        # Docker image for backend
├── Dockerfile.frontend       # Docker image for frontend
├── docker-compose.yml        # Docker compose configuration
├── render.yaml               # Render blueprint configuration
├── vercel.json               # Vercel deployment configuration
├── requirements.txt          # Root Python dependencies
└── README.md
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- API key for Groq (`gsk_...`)

---

### Local Development

#### 1. Clone Repository
```bash
git clone https://github.com/NiDHiN-1908/ragnoviq-enterprise-rag-assistant.git
cd ragnoviq-enterprise-rag-assistant
```

#### 2. Configure Environment (`.env`)
```bash
cp .env.example .env
```
Edit `.env`:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
ENVIRONMENT=development
```

#### 3. Run Application (1-Click)

##### Option A: Python Launcher (Recommended)
```bash
python start.py
```

##### Option B: Windows Batch Script
Double-click `run.bat`

##### Option C: Dedicated Backend Launcher
```bash
python run_backend.py
```

- **Frontend Chat UI**: `http://localhost:3000`
- **Backend API Server**: `http://localhost:8000`
- **Swagger API Docs**: `http://localhost:8000/docs`

---

## 🐳 Docker Deployment

```bash
docker-compose up --build -d
```
Access the application at `http://localhost:3000`.

---

## 📚 API Endpoints

### Ingestion
- `POST /api/v1/ingest/website` — Submit website URL for crawling and indexing
- `GET /api/v1/ingest/websites` — List all indexed websites with chunk metrics
- `GET /api/v1/ingest/status/{website_id}` — Get ingestion task progress
- `DELETE /api/v1/ingest/website/{website_id}` — Delete website and remove vectors

### Chat
- `POST /api/v1/chat/query` — Submit question and generate grounded RAG answer
- `GET /api/v1/chat/history/{session_id}` — Retrieve conversation session history
- `DELETE /api/v1/chat/session/{session_id}` — Clear chat session

### System
- `GET /api/v1/health` — Health check endpoint
- `GET /api/v1/status` — Comprehensive system metrics & FAISS index stats
- `GET /api/v1/sources` — List all indexed pages and text source chunks

---

## 📄 License
This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Authors
Built with ❤️ by **Nidhin S — Agentic AI Engineer**
