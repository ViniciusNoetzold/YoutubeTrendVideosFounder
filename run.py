import os
import sys
import subprocess
import webbrowser
import threading
import time

REQUIRED_PACKAGES = ["fastapi", "uvicorn", "httpx", "pydantic"]

def ensure_dependencies():
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
from app.services.database import init_db, get_tasks, create_task

def seed_initial_weekly_tasks():
    init_db()
    existing = get_tasks()
    if not existing:
        create_task(
            day_column="segunda",
            step_name="Pesquisar palavras chaves & Estudar temas",
            title="Mapear tendencias de IA & Produtividade da semana",
            niche="Tecnologia & IA",
            details="Usar a ferramenta para extrair tags de alto volume e 5 temas virais"
        )
        create_task(
            day_column="segunda",
            step_name="Roteiro",
            title="Escrever Gancho (0-15s) e Estrutura Principal",
            niche="Tecnologia & IA",
            details="Focar em retencao de publico com open loops nos primeiros minutos"
        )
        create_task(
            day_column="terca",
            step_name="Finalizar roteiro & Edicao",
            title="Revisao final do roteiro e Gravacao de B-Rolls",
            niche="Tecnologia & IA",
            details="Aplicar SFX e cortes rapidos a cada 5 segundos"
        )
        create_task(
            day_column="quarta",
            step_name="Terminar Edicao & Thumb/Titulo",
            title="Gerar 5 titulos CTR e Thumbnail de alto contraste",
            niche="Tecnologia & IA",
            details="Publicar no melhor horario (18:00h)"
        )
        print("[+] Cronograma semanal inicial configurado com sucesso!")

def open_browser():
    time.sleep(1.8)
    url = "http://localhost:8000"
    print(f"\n[+] Abrindo a aplicacao no navegador: {url}\n")
    webbrowser.open(url)

if __name__ == "__main__":
    seed_initial_weekly_tasks()
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("="*65)
    print(" YOUTUBE TREND & CONTENT FOUNDER - ONLINE")
    print(" Acesse no seu navegador: http://localhost:8000")
    print(" Pressione CTRL+C para encerrar o servidor")
    print("="*65)
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
