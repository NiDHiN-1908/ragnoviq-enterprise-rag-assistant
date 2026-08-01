"""
Dedicated Backend Launcher for RAGNoviq.
Ensures backend directory is on sys.path and runs the FastAPI Uvicorn server directly on port 8000.

Usage:
    python run_backend.py
"""

import sys
import os
from pathlib import Path

# Ensure backend directory is in sys.path regardless of execution directory
ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import socket
import uvicorn
from app.main import app


def is_port_free(host: str, port: int) -> bool:
    """Test if a host and port combination is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False


def free_port(port: int = 8000):
    """Find and kill any stale process bound to the specified port on Windows."""
    try:
        import subprocess
        netstat_bin = r"C:\Windows\System32\netstat.exe" if os.path.exists(r"C:\Windows\System32\netstat.exe") else "netstat"
        taskkill_bin = r"C:\Windows\System32\taskkill.exe" if os.path.exists(r"C:\Windows\System32\taskkill.exe") else "taskkill"

        cmd = f'"{netstat_bin}" -ano'
        output = subprocess.check_output(cmd, shell=True, text=True, errors="ignore")
        for line in output.strip().splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                if pid and pid.isdigit() and pid != "0" and int(pid) != os.getpid():
                    print(f"🧹 Terminating background process (PID {pid}) on port {port}...")
                    subprocess.run(f'"{taskkill_bin}" /F /PID {pid}', shell=True, capture_output=True)
    except Exception:
        pass


def run():
    print("=" * 60)
    print("🚀 Launching RAGNoviq FastAPI Backend Server...")
    print("=" * 60)
    
    ports_to_try = [8000, 8001, 8002, 8080]
    hosts_to_try = ["127.0.0.1", "0.0.0.0"]

    for port in ports_to_try:
        free_port(port)
        for host in hosts_to_try:
            if is_port_free(host, port):
                print(f"✅ Found available port! Binding to http://{host}:{port}")
                uvicorn.run(app, host=host, port=port, log_level="info")
                return

    print("❌ Could not bind to any port in [8000, 8001, 8002, 8080].")


if __name__ == "__main__":
    run()
