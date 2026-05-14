# RAGNoviq Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- API key from Groq (free at https://console.groq.com)

### Step 1: Get API Keys

1. **Groq API**
   - Go to https://console.groq.com
   - Create account (free tier available)
   - Create API key
   - Copy the key

### Step 2: Setup Backend

```bash
# Navigate to project
cd ragnoviq-rag-chatbot

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your API key
# Set GROQ_API_KEY=your_actual_key
nano .env  # or use your editor

# Run backend
python -m uvicorn app.main:app --reload
```

**Backend running at:** `http://localhost:8000`

### Step 3: Setup Frontend

```bash
# In new terminal, go to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend running at:** `http://localhost:3000`

## 🎯 First Use

### 1. Add a Website
- Go to Dashboard tab
- Click "Add Website"
- Enter URL: `https://openai.com` (or any website)
- Wait for indexing (shows progress)

### 2. Ask a Question
- Go to Chat tab
- Ask: "What is your mission?" (or relevant question)
- View answer with source citations

### 3. Explore Sources
- Go to Sources tab
- See all indexed websites
- View statistics

## 📊 System Endpoints

### Health Check
```bash
curl http://localhost:8000/api/v1/health
# Returns: {"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

### System Status
```bash
curl http://localhost:8000/api/v1/status
# Returns: Detailed metrics about indexed content
```

### List Websites
```bash
curl http://localhost:8000/api/v1/ingest/websites
# Returns: All indexed websites
```

## 🔧 Common Issues & Solutions

### Issue: "GROQ_API_KEY not found"
**Solution:** 
```bash
# Check .env file has the key
cat .env | grep GROQ_API_KEY

# If missing, add it
echo "GROQ_API_KEY=your_actual_key" >> .env
```

### Issue: "Frontend can't reach backend"
**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# If not, restart it:
python -m uvicorn app.main:app --reload
```

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Use different port
python -m uvicorn app.main:app --reload --port 8001

# Update frontend API URL if needed
# Edit frontend/src/services/api.js
```

### Issue: "Database errors"
**Solution:**
```bash
# Delete old database
rm data/ragnoviq.db

# Restart backend (recreates DB)
python -m uvicorn app.main:app --reload
```

## 📁 Project Structure Quick Reference

```
ragnoviq-rag-chatbot/
├── backend/app/          # Backend code
├── frontend/src/         # Frontend code
├── data/                 # Database and vectors
├── logs/                 # Application logs
├── README.md            # Full documentation
├── .env.example         # Environment template
├── requirements.txt     # Python packages
├── docker-compose.yml   # Docker setup
└── Dockerfile.*         # Container images
```

## 🐳 Docker (Alternative)

### Single Command Deployment

```bash
# Build and run everything
docker-compose up --build

# Access at http://localhost:3000

# Stop everything
docker-compose down
```

### Check Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔄 Full Workflow Example

### 1. Index a Website
```bash
curl -X POST http://localhost:8000/api/v1/ingest/website \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Returns website ID
```

### 2. Check Status
```bash
curl http://localhost:8000/api/v1/ingest/status/{website_id}

# Shows progress
```

### 3. Ask Question
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does this company do?",
    "session_id": "my_session"
  }'

# Returns answer with sources
```

## 📚 Documentation Index

- **README.md** - Complete project overview
- **ARCHITECTURE.md** - System design & data flow
- **DEPLOYMENT.md** - Production deployment guide
- **ROADMAP.md** - Development timeline & git commits
- **PORTFOLIO.md** - Career/interview materials
- **RESUME_SUMMARY.md** - Resume talking points

## 🎓 Learning Resources

### Understanding RAG
- [RAG Overview](https://python.langchain.com/docs/use_cases/question_answering/)
- [Vector Databases](https://www.pinecone.io/learn/vector-database/)
- [Embeddings](https://huggingface.co/tasks/sentence-similarity)

### Technologies Used
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

## 🚢 Next Steps

### Short-term
1. ✅ Local development setup
2. ✅ Index your first website
3. ✅ Test chat functionality
4. 🎯 Deploy to cloud (Render/Railway)
5. 🎯 Add more websites

### Medium-term
1. 🎯 Add user authentication
2. 🎯 Implement PDF ingestion
3. 🎯 Setup analytics dashboard
4. 🎯 Performance optimization

### Long-term
1. 🎯 Knowledge graph integration
2. 🎯 Custom embedding models
3. 🎯 Fine-tuning capabilities
4. 🎯 Multi-language support

## 💡 Tips & Tricks

### Faster Indexing
- Start with smaller websites
- Increase `MAX_PAGES_PER_DOMAIN` in .env
- Use `MAX_CRAWL_DEPTH=3` for speed

### Better Retrieval
- Adjust `CHUNK_SIZE` (default 512)
- Tune `SIMILARITY_THRESHOLD` (default 0.5)
- Increase `TOP_K_CHUNKS` (default 5)

### Dev Productivity
- Use hot reload: `--reload` flag
- Enable debug logging: `LOG_LEVEL=DEBUG`
- Watch vector DB size: `du -sh data/vector_db/`

## 📞 Getting Help

### Check Logs
```bash
# Backend logs
tail -f logs/ragnoviq.log

# Docker logs
docker-compose logs -f

# Browser console (Frontend)
F12 → Console tab
```

### Common Endpoints
- Health: `GET /api/v1/health`
- Status: `GET /api/v1/status`
- Models: `GET /api/v1/models`

### Debug Info
```bash
# Backend version
curl http://localhost:8000/

# Database info
sqlite3 data/ragnoviq.db ".tables"

# Vector DB stats
curl http://localhost:8000/api/v1/status | grep vector_db
```

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Backend runs without errors
- ✅ Frontend loads at localhost:3000
- ✅ Can add a website successfully
- ✅ Website gets indexed
- ✅ Chat returns answers with sources

## 🚀 Deployment Checklist

- [ ] Create GitHub repository
- [ ] Add `.env` file (not in git)
- [ ] Test locally with Docker
- [ ] Choose deployment platform
- [ ] Follow deployment guide
- [ ] Setup domain/SSL
- [ ] Configure monitoring
- [ ] Document deployment steps

## 📊 Performance Baseline

Expected performance on standard hardware:

| Operation | Time |
|-----------|------|
| Index 100-page site | 5-10 min |
| Generate embedding | 100ms |
| Vector search | 100-500ms |
| LLM response | 1-3 sec |
| Full chat response | 2-5 sec |

---

**Ready to get started? Choose:**
- 🚀 **Fastest**: Docker Compose (one command)
- 🛠️ **Most Control**: Local development
- ☁️ **Production**: Follow deployment guide

Happy building! 🎉
