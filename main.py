# ABOUTME: Main FastAPI application entry point
# ABOUTME: Sets up routers, templates, static files, and environment

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.stores import router as stores_router
from api.documents import router as documents_router
from api.query import router as query_router


# Load environment variables
load_dotenv()

# Verify API key
if not os.getenv('GEMINI_API_KEY'):
    raise ValueError('GEMINI_API_KEY not found. Copy .env.example to .env and add your API key')

# Initialize app
app = FastAPI(title='Gemini File Search', version='1.0.0')

# Setup templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

# Include routers
app.include_router(stores_router)
app.include_router(documents_router)
app.include_router(query_router)


@app.get('/', response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page with stores list"""
    return templates.TemplateResponse(request, 'dashboard.html')


@app.get('/stores/{store_id}', response_class=HTMLResponse)
async def store_detail(request: Request, store_id: str):
    """Store detail page with documents and query interface"""
    return templates.TemplateResponse(
        request,
        'store_detail.html',
        {'store_id': store_id}
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
