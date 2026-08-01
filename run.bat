@echo off
title RAGNoviq AI Chatbot Launcher
echo ========================================================
echo 🚀 Launching RAGNoviq Enterprise RAG AI Chatbot...
echo ========================================================
echo.

:: Check if .conda Python exists in project root
if exist "%~dp0.conda\python.exe" (
    set "PYTHON_EXE=%~dp0.conda\python.exe"
) else (
    set "PYTHON_EXE=python"
)

:: Launch Backend in separate window
start "RAGNoviq Backend (FastAPI)" cmd /k "cd /d %~dp0backend && "%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Launch Frontend in separate window
start "RAGNoviq Frontend (React/Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

:: Wait 3 seconds and open web browser
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================================
echo ✅ Both Backend & Frontend servers launched in new windows!
echo    • Frontend: http://localhost:3000
echo    • Backend:  http://localhost:8000/docs
echo ========================================================
echo.
pause
