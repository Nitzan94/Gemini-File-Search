# Gemini File Search

Web app for Google's Gemini file search API. Upload docs, semantic search, citations.

## Setup

```bash
# Clone
git clone https://github.com/Nitzan94/Gemini-File-Search.git
cd gemini-file-search

# Install
uv sync

# Configure
cp .env.example .env
# Add your GEMINI_API_KEY from https://aistudio.google.com/apikey

# Run
uv run python main.py
```

App: http://localhost:8000

## Features

- Create/manage file search stores
- Drag-drop file upload
- Semantic search with citations
- Document state tracking (pending/active/failed)
- Metadata filtering
- Store metrics (size, doc counts)

## API

- `POST /stores` - create store
- `GET /stores` - list stores
- `GET /stores/{id}` - get store
- `DELETE /stores/{id}` - delete store
- `POST /stores/{id}/upload` - upload file
- `GET /stores/{id}/documents` - list docs
- `DELETE /stores/{id}/documents/{doc_id}` - delete doc
- `POST /query` - semantic search

## Tests

```bash
uv run pytest
```

## Limits

Free tier: 1 GB storage, 100 MB per file

## Tech

- FastAPI
- Python 3.12
- google-genai SDK
- HTMX
- Jinja2
