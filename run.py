import os
import sys
import webbrowser
import threading
import time
import uvicorn

from app.services.database import init_db, get_tasks, create_task

def seed_initial_weekly_tasks():
    init_db()
    existing = get_tasks()
    if not existing:
        create_task(
            day_column="segunda",
            step_name="Pesquisar palavras chaves & Estudar temas",
            title="Mapear tendências de IA & Produtividade da semana",
            niche="Tecnologia & IA",
            details="Usar a ferramenta para extrair tags de alto volume e 5 temas virais"
        )
        create_task(
            day_column="segunda",
            step_name="Roteiro",
            title="Escrever Gancho (0-15s) e Estrutura Principal",
            niche="Tecnologia & IA",
            details="Focar em retenção de público com open loops nos primeiros minutos"
        )
        create_task(
            day_column="terca",
            step_name="Finalizar roteiro & Edição",
            title="Revisão final do roteiro e Gravação de B-Rolls",
            niche="Tecnologia & IA",
            details="Aplicar SFX e cortes rápidos a cada 5 segundos"
        )
        create_task(
            day_column="quarta",
            step_name="Terminar Edição & Thumb/Título",
            title="Gerar 5 títulos CTR e Thumbnail de alto contraste",
            niche="Tecnologia & IA",
            details="Publicar no melhor horário (18:00h)"
        )
        print("Tabela semanal inicial configurada com sucesso!")

def open_browser():
    time.sleep(1.5)
    url = "http://localhost:8000"
    print(f"\n[+] Abrindo a aplicacao no navegador: {url}\n")
    webbrowser.open(url)

if __name__ == "__main__":
    seed_initial_weekly_tasks()
    
    # Start browser in separate background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("="*65)
    print(" YOUTUBE TREND & CONTENT FOUNDER - ONLINE")
    print(" Acesse no seu navegador: http://localhost:8000")
    print(" Pressione CTRL+C para encerrar o servidor")
    print("="*65)
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
