import os, json, uvicorn
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.config import POPULAR_NICHES, NVIDIA_API_KEY
from app.services.database import (
    init_db, get_setting, set_setting,
    save_idea, get_saved_ideas, delete_idea,
    save_script, get_scripts, get_script_by_id, delete_script,
    create_task, get_tasks, update_task_status, delete_task
)
from app.services.scraper import (
    get_daily_google_trends, get_youtube_trending_feed,
    search_youtube_niche, get_youtube_autocomplete_keywords
)
from app.services.ai_service import (
    analyze_niche_and_keywords, generate_video_package,
    generate_full_script, call_nvidia_llm, get_active_api_key
)

init_db()

app = FastAPI(title='YouTube Trend & Content Founder', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

@app.get('/')
async def root():
    return FileResponse(os.path.join(static_dir, 'index.html'))

@app.get('/api/niches')
async def get_niches():
    return {'niches': POPULAR_NICHES}

@app.get('/api/trends/daily')
async def get_daily_trends(geo: str = 'BR'):
    google_trends = get_daily_google_trends(geo)
    youtube_trends = get_youtube_trending_feed(geo)
    return {
        'google_trends': google_trends,
        'youtube_trends': youtube_trends
    }

@app.get('/api/trends/niche')
async def get_niche_trends(
    query: str = Query(..., description='Niche query'),
    filter: str = 'relevant',
    content_type: str = 'all'
):
    videos = search_youtube_niche(query, date_filter=filter, content_type=content_type)
    autocomplete = get_youtube_autocomplete_keywords(query)
    return {
        'query': query,
        'filter': filter,
        'content_type': content_type,
        'videos': videos,
        'autocomplete_keywords': autocomplete
    }

@app.get('/api/keywords/autocomplete')
async def get_autocomplete(seed: str = Query(...)):
    keywords = get_youtube_autocomplete_keywords(seed)
    return {'seed': seed, 'keywords': keywords}

class AnalyzeNicheRequest(BaseModel):
    niche: str
    subniche: Optional[str] = ''
    trending_titles: Optional[List[str]] = []

@app.post('/api/ai/analyze-niche')
async def api_analyze_niche(req: AnalyzeNicheRequest):
    try:
        data = analyze_niche_and_keywords(req.niche, req.trending_titles or [], req.subniche or '')
        return {'status': 'success', 'data': data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class VideoPackageRequest(BaseModel):
    niche: str
    topic_or_title: str
    reference_urls: Optional[str] = ''

@app.post('/api/ai/video-package')
async def api_video_package(req: VideoPackageRequest):
    try:
        data = generate_video_package(req.niche, req.topic_or_title, req.reference_urls or '')
        return {'status': 'success', 'data': data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ScriptRequest(BaseModel):
    niche: str
    title: str
    notes_or_outline: Optional[str] = ''
    tone: Optional[str] = 'dinamico e envolvente'

@app.post('/api/ai/script')
async def api_generate_script(req: ScriptRequest):
    try:
        script_text = generate_full_script(req.niche, req.title, req.notes_or_outline or '', req.tone or 'dinamico')
        return {'status': 'success', 'script': script_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

@app.post('/api/ai/chat')
async def api_chat(req: ChatRequest):
    try:
        reply = call_nvidia_llm(req.messages, max_tokens=1500, temperature=0.7)
        return {'status': 'success', 'reply': reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Database CRUD
class SaveIdeaRequest(BaseModel):
    niche: str
    title: str
    keywords: Optional[str] = ''
    reference_urls: Optional[str] = ''
    hook: Optional[str] = ''
    notes: Optional[str] = ''

@app.get('/api/ideas')
async def api_get_ideas():
    return {'ideas': get_saved_ideas()}

@app.post('/api/ideas')
async def api_save_idea(req: SaveIdeaRequest):
    idea_id = save_idea(req.niche, req.title, req.keywords or '', req.reference_urls or '', req.hook or '', req.notes or '')
    return {'status': 'success', 'id': idea_id}

@app.delete('/api/ideas/{idea_id}')
async def api_delete_idea(idea_id: int):
    delete_idea(idea_id)
    return {'status': 'success'}

class SaveScriptRequest(BaseModel):
    niche: str
    title: str
    hook: Optional[str] = ''
    script_body: str
    cta: Optional[str] = ''
    thumbnail_concept: Optional[str] = ''
    titles_suggestions: Optional[str] = ''
    keywords: Optional[str] = ''
    idea_id: Optional[int] = None

@app.get('/api/scripts')
async def api_get_scripts():
    return {'scripts': get_scripts()}

@app.get('/api/scripts/{script_id}')
async def api_get_script(script_id: int):
    item = get_script_by_id(script_id)
    if not item:
        raise HTTPException(status_code=404, detail='Roteiro nao encontrado')
    return {'script': item}

@app.post('/api/scripts')
async def api_save_script(req: SaveScriptRequest):
    script_id = save_script(
        req.niche, req.title, req.hook or '', req.script_body,
        req.cta or '', req.thumbnail_concept or '',
        req.titles_suggestions or '', req.keywords or '', req.idea_id
    )
    return {'status': 'success', 'id': script_id}

@app.delete('/api/scripts/{script_id}')
async def api_delete_script(script_id: int):
    delete_script(script_id)
    return {'status': 'success'}

# Production Tasks (Weekly Schedule)
class CreateTaskRequest(BaseModel):
    day_column: str # 'segunda', 'terca', 'quarta'
    step_name: str
    title: str
    niche: Optional[str] = ''
    details: Optional[str] = ''
    reference_links: Optional[str] = ''

class UpdateTaskRequest(BaseModel):
    status: str
    day_column: Optional[str] = None

@app.get('/api/tasks')
async def api_get_tasks():
    return {'tasks': get_tasks()}

@app.post('/api/tasks')
async def api_create_task(req: CreateTaskRequest):
    task_id = create_task(req.day_column, req.step_name, req.title, req.niche or '', req.details or '', req.reference_links or '')
    return {'status': 'success', 'id': task_id}

@app.put('/api/tasks/{task_id}')
async def api_update_task(task_id: int, req: UpdateTaskRequest):
    update_task_status(task_id, req.status, req.day_column)
    return {'status': 'success'}

@app.delete('/api/tasks/{task_id}')
async def api_delete_task(task_id: int):
    delete_task(task_id)
    return {'status': 'success'}

class SettingsRequest(BaseModel):
    nvidia_api_key: Optional[str] = None

@app.get('/api/settings')
async def api_get_settings():
    active_key = get_active_api_key()
    masked = active_key[:8] + '...' + active_key[-4:] if len(active_key) > 12 else active_key
    return {'has_nvidia_key': bool(active_key), 'masked_key': masked}

@app.post('/api/settings')
async def api_save_settings(req: SettingsRequest):
    if req.nvidia_api_key:
        set_setting('nvidia_api_key', req.nvidia_api_key.strip())
    return {'status': 'success'}

@app.get('/api/status')
async def api_status():
    return {'status': 'online', 'api_configured': bool(get_active_api_key())}
