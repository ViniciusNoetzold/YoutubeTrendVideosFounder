import os
import sys
import subprocess
import webbrowser
import threading
import time

IS_RENDER = bool(os.environ.get("RENDER"))

REQUIRED_PACKAGES = ["fastapi", "uvicorn", "httpx", "pydantic"]

def ensure_dependencies():
    if IS_RENDER:
        return
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        print(f"[*] Instalando dependencias necessarias: {', '.join(missing)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
            print("[+] Dependencias instaladas com sucesso!\n")
        except Exception as e:
            print(f"[!] Erro ao instalar dependencias: {e}")
            print("[!] Tente rodar manualmente: pip install -r requirements.txt")

ensure_dependencies()

import uvicorn
from app.services.database import init_db, seed_initial_weekly_tasks

def open_browser(port):
    time.sleep(1.8)
    url = f"http://localhost:{port}"
    print(f"\n[+] Abrindo a aplicacao no navegador: {url}\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    init_db()
    seed_initial_weekly_tasks()
    
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    if not IS_RENDER and not os.environ.get("CI"):
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    print("="*65)
    print(" YOUTUBE TREND & CONTENT FOUNDER - MEZZOLD STUDIO")
    print(f" Servidor iniciado em: http://{host}:{port}")
    print(" Pressione CTRL+C para encerrar o servidor")
    print("="*65)
    
    uvicorn.run("app.main:app", host=host, port=port, log_level="info")
