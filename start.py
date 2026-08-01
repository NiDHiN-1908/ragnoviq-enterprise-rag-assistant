"""
Shortcut launcher script for RAGNoviq Enterprise AI Chatbot.
Launches both Backend (FastAPI) and Frontend (Vite React) concurrently and opens the browser.

Usage:
    python start.py
"""

import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()


def main():
    print("=" * 60)
    print("🚀 Starting RAGNoviq Enterprise AI Chatbot...")
    print("=" * 60)

    # Auto-detect project local .conda environment if present
    conda_python = ROOT_DIR / ".conda" / "python.exe"
    python_bin = str(conda_python) if conda_python.exists() else sys.executable

    use_shell = os.name == "nt"

    # 1. Start Backend
    backend_dir = ROOT_DIR / "backend"
    print("\n📦 Launching FastAPI Backend on http://localhost:8000 ...")
    backend_cmd = [
        python_bin,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]
    backend_process = subprocess.Popen(backend_cmd, cwd=str(backend_dir), shell=use_shell)

    # 2. Start Frontend
    frontend_dir = ROOT_DIR / "frontend"
    print("💻 Launching React Vite Frontend...")
    frontend_process = subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir), shell=use_shell)

    # 3. Wait and open browser
    print("\n⏳ Initializing services...")
    time.sleep(3)
    webbrowser.open("http://localhost:3000")

    print("\n" + "=" * 60)
    print("✅ RAGNoviq Application is Running!")
    print("   • Frontend Chat UI:   http://localhost:3000")
    print("   • Backend API Server: http://localhost:8000")
    print("   • Swagger Docs:       http://localhost:8000/docs")
    print("=" * 60)
    print("\n[Press Ctrl+C in this terminal to stop both servers]\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping RAGNoviq servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("👋 All services stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
