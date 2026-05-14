# Deployment Guide

## Deployment Options

### 1. Local Development

**Prerequisites**
- Python 3.11+
- Node.js 18+
- SQLite (included with Python)

**Steps**
```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access at `http://localhost:3000`

### 2. Docker Local

**Prerequisites**
- Docker
- Docker Compose

**Steps**
```bash
# Copy environment file
cp .env.example .env
# Edit .env with API keys

# Build and run
docker-compose up --build

# Access at http://localhost:3000
```

**Useful commands**
```bash
docker-compose logs -f backend      # View backend logs
docker-compose logs -f frontend     # View frontend logs
docker-compose restart backend      # Restart service
docker-compose down -v              # Remove everything including volumes
```

### 3. Render.com Deployment

**Setup Steps**

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ragnoviq-rag-chatbot.git
   git push -u origin main
   ```

2. **Create Backend Service**
   - Go to render.com and connect GitHub
   - New → Web Service
   - Select repository
   - **Build Command**: `pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0`
   - **Environment Variables**:
     ```
     GROQ_API_KEY=your_key
     GOOGLE_API_KEY=your_key
     ENVIRONMENT=production
     DATABASE_URL=sqlite:///./data/ragnoviq.db
     ```
   - **Disk**: Add persistent disk at /app/data

3. **Create Frontend Service**
   - New → Static Site
   - Select repository
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

4. **Update Frontend API URL**
   - In frontend, update API base URL to backend service URL
   - Set environment variable: `VITE_API_URL=https://your-backend.onrender.com`

### 4. Railway.app Deployment

**Setup Steps**

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login and Create Project**
   ```bash
   railway login
   railway init
   ```

3. **Configure Services**
   ```bash
   # Create backend service
   railway add
   # Select Python
   
   # Create frontend service  
   railway add
   # Select Node.js
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set GROQ_API_KEY=your_key
   railway variables set ENVIRONMENT=production
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### 5. AWS EC2 Deployment

**Prerequisites**
- AWS account
- EC2 instance (t3.medium or larger)
- Ubuntu 22.04

**Setup Steps**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3.11 python3-pip python3-venv

# Install Node
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Git
sudo apt install -y git

# Clone repository
git clone https://github.com/yourusername/ragnoviq-rag-chatbot.git
cd ragnoviq-rag-chatbot

# Setup backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Edit with your keys

# Setup frontend
cd frontend
npm install
npm run build
cd ..

# Install systemd services
sudo tee /etc/systemd/system/ragnoviq-backend.service > /dev/null <<EOF
[Unit]
Description=RAGNoviq Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ragnoviq-rag-chatbot
ExecStart=/home/ubuntu/ragnoviq-rag-chatbot/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start services
sudo systemctl enable ragnoviq-backend
sudo systemctl start ragnoviq-backend

# Install Nginx
sudo apt install -y nginx

# Configure Nginx (reverse proxy)
sudo tee /etc/nginx/sites-available/default > /dev/null <<'EOF'
upstream backend {
    server localhost:8000;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # Frontend
    location / {
        root /home/ubuntu/ragnoviq-rag-chatbot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo systemctl restart nginx

# Check status
sudo systemctl status ragnoviq-backend
```

Access at `http://your-instance-ip`

### 6. DigitalOcean App Platform

**Setup Steps**

1. **Create GitHub Repository** (same as Render)

2. **Deploy with App Platform**
   - Go to DigitalOcean console
   - Create → App
   - Connect GitHub repository
   - Configure services:
     - Backend (Python)
       - Build: `pip install -r requirements.txt`
       - Run: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
     - Frontend (Node)
       - Build: `cd frontend && npm install && npm run build`
       - Run: `cd frontend && npm run preview`

3. **Setup Database**
   - Add SQLite-compatible alternative (e.g., PostgreSQL for production)
   - Update DATABASE_URL

### 7. Vercel + API Routing

**For Frontend Only (if using external API)**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

**Create `vercel.json`** for API routing
```json
{
  "rewrites": [
    {
      "source": "/api/:match*",
      "destination": "https://your-backend-api.com/api/:match*"
    }
  ]
}
```

## Production Checklist

- [ ] Set DEBUG=False in .env
- [ ] Set ENVIRONMENT=production
- [ ] Configure CORS_ORIGINS properly
- [ ] Setup SSL/TLS certificates
- [ ] Enable logging
- [ ] Setup monitoring and alerts
- [ ] Configure database backups
- [ ] Setup rate limiting
- [ ] Configure API key management
- [ ] Enable security headers
- [ ] Setup domain name
- [ ] Configure email for errors
- [ ] Setup Redis for caching (optional)
- [ ] Configure CDN for static files
- [ ] Setup monitoring dashboard
- [ ] Test disaster recovery
- [ ] Document deployment process
- [ ] Setup CI/CD pipeline

## Monitoring & Logging

### Application Logs
```bash
# Local
tail -f logs/ragnoviq.log

# Docker
docker-compose logs -f backend

# EC2/Server
journalctl -u ragnoviq-backend -f
```

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Full system
curl http://localhost:8000/api/v1/status
```

### Performance Monitoring
- Monitor CPU and memory usage
- Track API response times
- Monitor vector DB size
- Track database queries
- Monitor API key usage

## Scaling Strategies

### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Share FAISS index across instances
- Use shared SQLite or upgrade to PostgreSQL

### Vertical Scaling
- Increase instance CPU/RAM
- Optimize query performance
- Implement caching layers
- Batch process embeddings

### Cost Optimization
- Use spot instances
- Implement auto-scaling
- Cache frequently accessed data
- Optimize model serving
- Use CDN for static files

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify database
sqlite3 data/ragnoviq.db ".tables"

# Test API key
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
```

### Frontend can't reach backend
```bash
# Check CORS
curl -H "Origin: http://localhost:3000" -i http://localhost:8000/api/v1/health

# Check proxy
curl http://localhost:8000/api/v1/health
```

### Low performance
- Check vector DB size
- Monitor database queries
- Check embedding generation time
- Optimize chunk size
- Consider pagination

## Rollback Procedure

```bash
# Git rollback
git revert <commit-hash>
git push origin main

# Docker rollback
docker-compose down
git checkout <previous-version>
docker-compose up --build

# Check health
curl http://localhost:3000
```
