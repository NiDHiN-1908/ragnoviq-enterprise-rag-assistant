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


def get_python_executable():
    conda_python = ROOT_DIR / ".conda" / "python.exe"
    if conda_python.exists():
        try:
            res = subprocess.run([str(conda_python), "-c", "import uvicorn"], capture_output=True)
            if res.returncode == 0:
                return str(conda_python)
        except Exception:
            pass
    return sys.executable


def main():
    print("=" * 60)
    print("🚀 Starting RAGNoviq Enterprise AI Chatbot...")
    print("=" * 60)

    python_bin = get_python_executable()

    use_shell = os.name == "nt"

    # 1. Start Backend
    print("\n📦 Launching FastAPI Backend on http://localhost:8000 ...")
    backend_cmd = f'"{python_bin}" "{ROOT_DIR / "run_backend.py"}"'
    backend_process = subprocess.Popen(backend_cmd, cwd=str(ROOT_DIR), shell=True)

    # 2. Start Frontend
    frontend_dir = ROOT_DIR / "frontend"
    print("💻 Launching React Vite Frontend...")
    frontend_cmd = "npm run dev"
    frontend_process = subprocess.Popen(frontend_cmd, cwd=str(frontend_dir), shell=True)

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
