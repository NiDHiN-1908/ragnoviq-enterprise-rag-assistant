# RAGNoviq PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🚀 Launching RAGNoviq Enterprise RAG AI Chatbot..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend Process
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ScriptDir\backend'; Write-Host '📦 Starting Backend...'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Start Frontend Process
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ScriptDir\frontend'; Write-Host '💻 Starting Frontend...'; npm run dev"

# Wait and Open Browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host "✅ Backend & Frontend servers launched!" -ForegroundColor Green
Write-Host "   • UI: http://localhost:3000" -ForegroundColor Yellow
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
