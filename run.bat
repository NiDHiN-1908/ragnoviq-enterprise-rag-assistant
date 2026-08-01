@echo off
title RAGNoviq AI Chatbot Launcher
echo ========================================================
echo 🚀 Launching RAGNoviq Enterprise RAG AI Chatbot...
echo ========================================================
echo.

:: Launch Backend in separate window
start "RAGNoviq Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Launch Frontend in separate window
start "RAGNoviq Frontend (React/Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

:: Wait 3 seconds and open web browser
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================================
echo ✅ Both Backend & Frontend servers launched in new windows!
echo    • Frontend: http://localhost:5173
echo    • Backend:  http://localhost:8000/docs
echo ========================================================
echo.
pause
