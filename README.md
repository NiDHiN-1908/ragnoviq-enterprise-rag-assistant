# RAGNoviq - Enterprise RAG Website Knowledge Assistant

A production-grade Retrieval-Augmented Generation (RAG) system for creating intelligent knowledge assistants from website content.

## 🚀 Features

### Core RAG Pipeline
- **Website Crawling**: Recursive crawling with depth control and internal link discovery
- **Smart Content Extraction**: HTML parsing, boilerplate removal, and text cleaning
- **Semantic Chunking**: Intelligent text splitting with overlap for better retrieval
- **Embedding Generation**: Using sentence-transformers for semantic embeddings
- **Vector Search**: FAISS-based similarity search for fast retrieval
- **Grounded Generation**: LLM responses based strictly on indexed content
- **Source Citation**: Every answer includes source references

### Multi-Source Indexing
- Support for multiple websites
- Per-website filtering and management
- Real-time indexing progress tracking

### Conversational Interface
- Chat-style Q&A interface
- Session-based conversation history
- Typing animations and loading indicators
- Source citations below answers

### Admin Dashboard
- Website management (add, delete, monitor)
- Indexing progress tracking
- Statistics and metrics
- Source browsing

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: SQLite + SQLAlchemy ORM
- **Vector DB**: FAISS
- **Embeddings**: sentence-transformers
- **LLM**: Groq API or Google Gemini
- **Web Scraping**: BeautifulSoup + Requests

### Frontend Stack
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **HTTP Client**: Axios

## 📁 Project Structure

```
ragnoviq-rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── services/         # Business logic (crawler, chunker, RAG, etc.)
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── db/               # Database connection and repositories
│   │   ├── vector_db/        # FAISS vector database
│   │   ├── utils/            # Utility functions
│   │   ├── core/             # Configuration and logging
│   │   └── main.py           # FastAPI application entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   ├── styles/           # CSS
│   │   └── store.js          # Zustand store
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- API keys for Groq or Google Gemini

### Local Development

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ragnoviq-rag-chatbot.git
cd ragnoviq-rag-chatbot
```

#### 2. Setup Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Initialize database
python -c "from app.db.database import init_db; init_db()"

# Run backend
python -m uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

#### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

Access the application at `http://localhost:3000`

## 🔑 Environment Variables

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=mixtral-8x7b-32768

# Embeddings
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Database
VECTOR_DB_TYPE=faiss
VECTOR_DB_PATH=./data/vector_db
CHUNK_SIZE=512
CHUNK_OVERLAP=102

# Web Scraping
MAX_CRAWL_DEPTH=5
MAX_PAGES_PER_DOMAIN=100
REQUEST_TIMEOUT=30

# Database
DATABASE_URL=sqlite:///./data/ragnoviq.db

# Frontend
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 📚 API Endpoints

### Ingestion
- `POST /api/v1/ingest/website` - Submit website for indexing
- `GET /api/v1/ingest/status/{website_id}` - Get ingestion progress
- `DELETE /api/v1/ingest/website/{website_id}` - Delete website
- `GET /api/v1/ingest/websites` - List all websites

### Chat
- `POST /api/v1/chat/query` - Submit question and get response
- `GET /api/v1/chat/history/{session_id}` - Get chat history
- `DELETE /api/v1/chat/session/{session_id}` - Clear session

### System
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - System status and metrics
- `GET /api/v1/sources` - List indexed sources
- `GET /api/v1/models` - Get model information

## 🔄 RAG Pipeline Flow

1. **Website Submission** → User submits URL via dashboard
2. **Crawling** → Recursive crawl with depth control
3. **Parsing** → Extract clean text, remove boilerplate
4. **Chunking** → Semantic text splitting with overlap
5. **Embedding** → Generate semantic embeddings
6. **Indexing** → Store in FAISS vector database
7. **Query** → User asks question
8. **Retrieval** → Find top-K similar chunks
9. **Generation** → LLM generates grounded response
10. **Citation** → Add source references

## 🔒 Security Features

- Environment variable isolation for API keys
- Input validation on all endpoints
- CORS protection
- Rate limiting capability
- Secure session management
- Logging of all operations

## 🚀 Deployment

### Render.com
```bash
# Build and deploy
git push origin main
# Render auto-deploys from git
```

### Railway.app
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway up
```

### AWS EC2/Heroku
```bash
# Push to repository
git push heroku main

# Check logs
heroku logs --tail
```

## 📊 Performance Optimization

- Batch embedding generation
- Vector DB indexing
- Query result caching
- Connection pooling
- Async processing
- Request timeout handling

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm run test
```

## 📝 Database Schema

### Core Tables
- **websites**: Indexed websites metadata
- **web_pages**: Crawled pages
- **text_chunks**: Content chunks with metadata
- **chat_messages**: Conversation history
- **ingestion_tasks**: Tracking ingestion progress
- **api_keys**: API key management
- **system_logs**: Application logging

## 🛣️ Roadmap

- [ ] PDF file ingestion support
- [ ] Multi-language support
- [ ] Advanced filtering and metadata
- [ ] User authentication and authorization
- [ ] Usage analytics and dashboard
- [ ] Streaming responses
- [ ] RAG evaluation metrics
- [ ] Custom embedding models
- [ ] Knowledge graph integration
- [ ] Fine-tuning capabilities

## 📚 Documentation

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [API Documentation](./docs/API.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🤖 Authors

Built with ❤️ by AI Engineers

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@ragnoviq.ai

## 🙏 Acknowledgments

- FastAPI for excellent async framework
- sentence-transformers for embeddings
- FAISS for efficient similarity search
- React and Vite for frontend
- All open-source contributors
