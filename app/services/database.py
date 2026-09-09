import sqlite3
import json
from app.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        niche TEXT NOT NULL,
        title TEXT NOT NULL,
        keywords TEXT,
        reference_urls TEXT,
        hook TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER,
        niche TEXT NOT NULL,
        title TEXT NOT NULL,
        hook TEXT,
        script_body TEXT,
        cta TEXT,
        thumbnail_concept TEXT,
        titles_suggestions TEXT,
        keywords TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS production_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_column TEXT NOT NULL,
        step_name TEXT NOT NULL,
        title TEXT NOT NULL,
        niche TEXT,
        details TEXT,
        reference_links TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    seed_initial_weekly_tasks()

def get_setting(key, default=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def save_idea(niche, title, keywords="", reference_urls="", hook="", notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO saved_ideas (niche, title, keywords, reference_urls, hook, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (niche, title, keywords, reference_urls, hook, notes))
    idea_id = c.lastrowid
    conn.commit()
    conn.close()
    return idea_id

def get_saved_ideas():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM saved_ideas ORDER BY created_at DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def delete_idea(idea_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM saved_ideas WHERE id = ?", (idea_id,))
    conn.commit()
    conn.close()

def save_script(niche, title, hook, script_body, cta="", thumbnail_concept="", titles_suggestions="", keywords="", idea_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO scripts (idea_id, niche, title, hook, script_body, cta, thumbnail_concept, titles_suggestions, keywords)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (idea_id, niche, title, hook, script_body, cta, thumbnail_concept, titles_suggestions, keywords))
    script_id = c.lastrowid
    conn.commit()
    conn.close()
    return script_id

def get_scripts():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM scripts ORDER BY created_at DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_script_by_id(script_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_script(script_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM scripts WHERE id = ?", (script_id,))
    conn.commit()
    conn.close()

def create_task(day_column, step_name, title, niche="", details="", reference_links=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO production_tasks (day_column, step_name, title, niche, details, reference_links, status)
    VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (day_column, step_name, title, niche, details, reference_links))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM production_tasks ORDER BY created_at ASC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def update_task_status(task_id, status, day_column=None):
    conn = get_connection()
    c = conn.cursor()
    if day_column:
        c.execute("UPDATE production_tasks SET status = ?, day_column = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, day_column, task_id))
    else:
        c.execute("UPDATE production_tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM production_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def seed_initial_weekly_tasks():
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

