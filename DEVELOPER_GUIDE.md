# Developer Guide - Gemini File Search Application

Comprehensive technical guide for understanding and extending the Gemini File Search web application.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Key Patterns](#key-patterns)
- [Common Tasks](#common-tasks)
- [Testing Strategy](#testing-strategy)
- [Deployment](#deployment)

## Architecture Overview

**Technology Stack:**
- **Backend:** FastAPI (Python async web framework)
- **SDK:** google-genai (Gemini File Search API client)
- **Frontend:** Vanilla JavaScript + HTMX patterns
- **Templating:** Jinja2
- **Package Management:** uv (modern Python packaging)

**Core Architecture:**
```
┌─────────────┐
│   Browser   │
│  (HTML/JS)  │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────┐
│   FastAPI Routes    │
│ ┌─────────────────┐ │
│ │ stores.py       │ │  Store CRUD
│ │ documents.py    │ │  Upload/manage
│ │ query.py        │ │  Semantic search
│ └────────┬────────┘ │
│          │          │
│    ┌─────▼─────┐    │
│    │ client.py │    │  Singleton wrapper
│    └─────┬─────┘    │
└──────────┼──────────┘
           │ SDK calls
           ▼
    ┌──────────────┐
    │  Gemini API  │
    │ File Search  │
    └──────────────┘
```

**Key Design Principles:**
1. **Singleton Client:** Single GenAI client instance reused across requests
2. **Async Operations:** Long-running uploads use operation polling
3. **Separation of Concerns:** API routes separate from business logic
4. **Safe Attribute Access:** Citations extracted with hasattr checks
5. **Tempfile Pattern:** Multipart uploads use temp files with cleanup

## Project Structure

```
gemini-file-search/
├── main.py                 # FastAPI app entry point
├── api/
│   ├── __init__.py
│   ├── client.py          # GeminiClient singleton wrapper
│   ├── stores.py          # Store CRUD routes (/api/stores)
│   ├── documents.py       # Document upload/manage routes
│   └── query.py           # Semantic search routes (/api/query)
├── templates/
│   ├── base.html          # Base template with CSS
│   ├── dashboard.html     # Store list page
│   └── store_detail.html  # Chat interface + file upload
├── static/
│   └── (currently empty - JS inline in templates)
├── tests/
│   └── test_api.py        # Integration tests
├── .env.example           # Environment variables template
├── pyproject.toml         # uv project configuration
└── README.md              # User documentation
```

## Core Components

### 1. GeminiClient Singleton (api/client.py)

**Purpose:** Reuse GenAI client connection across all requests

**Pattern:**
```python
class GeminiClient:
    _instance: Optional['GeminiClient'] = None
    _client: Optional[genai.Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Key Methods:**
- `create_store()` - Create document container
- `list_stores()` - List all stores with metrics
- `upload_document()` - Upload file with metadata
- `list_documents()` - List docs in store
- `search()` - Semantic query with citations
- `get_operation()` - Poll upload status

**Why Singleton:**
- Prevents redundant API client initialization
- Reuses connection across requests
- Thread-safe instance management

### 2. Store Router (api/stores.py)

**Routes:**
- `POST /api/stores` - Create store
- `GET /api/stores` - List stores
- `GET /api/stores/{store_id}` - Get store details
- `DELETE /api/stores/{store_id}` - Delete store

**Key Pattern - Error Handling:**
```python
@router.post('')
async def create_store(request: CreateStoreRequest):
    try:
        client = GeminiClient()
        store = client.create_store(display_name=request.display_name)
        return {'name': store.name, 'display_name': store.display_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Document Router (api/documents.py)

**Routes:**
- `POST /api/stores/{store_id}/upload` - Upload file
- `GET /api/stores/{store_id}/documents` - List documents
- `DELETE /api/stores/{store_id}/documents/{doc_id}` - Delete document
- `GET /api/stores/operations/{operation_id}` - Poll operation status

**Critical Pattern - Tempfile Upload:**
```python
with tempfile.NamedTemporaryFile(
    delete=False,
    suffix=os.path.splitext(file.filename)[1]
) as tmp:
    content = await file.read()
    tmp.write(content)
    tmp_path = tmp.name

# Upload to Gemini
operation = client.upload_document(file_path=tmp_path, ...)

# Always clean up
os.unlink(tmp_path)
```

**Why This Pattern:**
1. FastAPI's UploadFile is async - can't pass directly to SDK
2. Preserves file extension for format detection
3. Explicit cleanup prevents temp file buildup
4. Returns operation for frontend polling

### 4. Query Router (api/query.py)

**Routes:**
- `POST /api/query` - Semantic search with citations

**Request Model:**
```python
class QueryRequest(BaseModel):
    query: str
    store_ids: list[str]
    metadata_filter: Optional[str] = None
    model: str = 'gemini-2.5-flash'
```

**Response Format:**
```json
{
  "text": "The Q2 revenue was $50M...",
  "citations": [
    {"title": "Q2 Report", "uri": "gs://..."}
  ]
}
```

**Safe Citation Extraction:**
```python
# Always check attributes exist
if hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'grounding_metadata'):
        # Extract citations...
```

### 5. Chat Interface (templates/store_detail.html)

**UI Components:**
- Drag-drop upload zone
- Document list with state badges
- Chat interface (user messages right/blue, AI left/white)
- Typing indicator with animation
- Citations display inline

**Key JavaScript Functions:**
```javascript
sendMessage()       // Send query, show typing indicator
addMessage()        // Add user/AI message to chat
pollOperation()     // Poll upload until done
handleDrop()        // Drag-drop file upload
```

**Auto-scroll Pattern:**
```javascript
function scrollToBottom() {
    const container = document.querySelector('.messages');
    container.scrollTop = container.scrollHeight;
}
```

## Data Flow

### Upload Flow

```
1. User drops file → handleDrop()
2. FormData created → POST /api/stores/{id}/upload
3. FastAPI saves to tempfile
4. SDK upload initiated → returns Operation
5. Tempfile cleaned up
6. Frontend polls /api/stores/operations/{op_id}
7. When operation.done → refresh document list
8. Document STATE_PENDING → STATE_ACTIVE (30-60s)
```

### Query Flow

```
1. User types query → sendMessage()
2. Add user message to chat (blue bubble)
3. Show typing indicator (animated dots)
4. POST /api/query with store_ids
5. GeminiClient.search() → SDK generate_content
6. Extract text + citations
7. Remove typing indicator
8. Add AI message to chat (white bubble)
9. Display citations below message
10. Auto-scroll to bottom
```

### Store Lifecycle

```
Create Store
    ↓
Upload Documents (STATE_PENDING)
    ↓
Wait for Processing (30-60s)
    ↓
Documents Active (STATE_ACTIVE)
    ↓
Query Documents (semantic search)
    ↓
Delete Store (force=True if has docs)
```

## Key Patterns

### 1. BASE_DIR Pattern for Static Files

**Problem:** Relative paths fail with uvicorn
**Solution:**
```python
from pathlib import Path

BASE_DIR = Path(__file__).parent
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')))
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
```

### 2. API Route Prefixing

**Problem:** API and page routes conflicted (/stores/{id})
**Solution:**
```python
# API routes
router = APIRouter(prefix='/api/stores')

# Page routes separate
@app.get('/stores/{store_id}')  # Returns HTML
```

### 3. SDK Method Paths

**Correct:**
```python
# Documents are sub-resource
client.file_search_stores.documents.list(parent='fileSearchStores/id')
client.file_search_stores.documents.get(name='fileSearchStores/id/documents/doc-id')

# Operations at top level
client.operations.get(name='fileSearchStores/id/upload/operations/op-id')
```

**Incorrect:**
```python
client.file_search_stores.list_documents()  # ❌ No such method
client.file_search_stores.get_operation()  # ❌ Wrong path
```

### 4. Document State Handling

**Always check state before querying:**
```python
doc = client.get_document(name='...')
if doc.state == 'STATE_ACTIVE':
    # Ready to query
elif doc.state == 'STATE_PENDING':
    # Still processing, wait
elif doc.state == 'STATE_FAILED':
    # Processing failed, check format
```

### 5. Citation Safety

**Never assume citations exist:**
```python
result = {'text': response.text, 'citations': []}

if hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'grounding_metadata'):
        grounding = candidate.grounding_metadata
        if hasattr(grounding, 'grounding_chunks'):
            for chunk in grounding.grounding_chunks:
                if hasattr(chunk, 'retrieved_context'):
                    ctx = chunk.retrieved_context
                    result['citations'].append({
                        'title': getattr(ctx, 'title', ''),
                        'uri': getattr(ctx, 'uri', '')
                    })
```

## Common Tasks

### Adding New Query Features

1. **Modify QueryRequest model** (api/query.py):
```python
class QueryRequest(BaseModel):
    query: str
    store_ids: list[str]
    metadata_filter: Optional[str] = None
    model: str = 'gemini-2.5-flash'
    temperature: Optional[float] = None  # New parameter
```

2. **Update search call:**
```python
config = types.GenerateContentConfig(
    tools=[types.Tool(file_search=...)],
    temperature=request.temperature  # Pass to SDK
)
```

3. **Update frontend:**
```javascript
body: JSON.stringify({
    query: query,
    store_ids: [storeId],
    temperature: 0.7  // Add to request
})
```

### Adding Metadata Filters UI

1. **Add metadata form** (store_detail.html):
```html
<select id="metadata-filter">
    <option value="">All Documents</option>
    <option value="category=reports">Reports Only</option>
    <option value="year=2024">2024 Only</option>
</select>
```

2. **Include in query:**
```javascript
const filter = document.getElementById('metadata-filter').value;
body: JSON.stringify({
    query: query,
    store_ids: [storeId],
    metadata_filter: filter || null
})
```

### Debugging Upload Issues

1. **Check operation status:**
```python
operation = client.get_operation(name='...')
print(f'Done: {operation.done}')
```

2. **Check document state:**
```python
doc = client.get_document(name='...')
print(f'State: {doc.state}')
```

3. **Verify file format:**
- PDF, DOCX, PPTX, XLSX, Python, JS, Go, C++, CSV, JSON, HTML, MD, ZIP
- Max 100MB per file
- Check encoding (UTF-8 recommended)

### Adding Custom Store Metadata

Currently stores only have `display_name`. To add custom metadata:

1. **Extend create_store:**
```python
# Note: SDK doesn't support custom store metadata
# Use naming convention: "ProjectName - Category - Date"
store = client.create_store(
    display_name=f'{project} - {category} - {date}'
)
```

2. **Parse on retrieval:**
```python
parts = store.display_name.split(' - ')
project, category, date = parts if len(parts) == 3 else (parts[0], '', '')
```

## Testing Strategy

### Integration Tests (tests/test_api.py)

**Fixture Pattern:**
```python
@pytest.fixture
def test_store(client):
    """Create test store, yield ID, clean up after"""
    response = client.post('/api/stores', json={'display_name': 'Test'})
    store_id = response.json()['name'].split('/')[1]

    yield store_id

    client.delete(f'/api/stores/{store_id}?force=true')
```

**Running Tests:**
```bash
# All tests
uv run pytest tests/ -v

# Specific test
uv run pytest tests/test_api.py::test_create_store -v

# With output
uv run pytest tests/ -v -s
```

**Test Coverage:**
- ✅ Store CRUD operations
- ✅ Document upload/list/delete
- ✅ Page rendering
- ✅ API error handling

## Deployment

### Environment Setup

**.env file:**
```
GEMINI_API_KEY=your_key_here
```

**Get API key:** https://aistudio.google.com/apikey

### Local Development

```bash
# Install dependencies
uv sync

# Run dev server
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8001

# Run tests
uv run pytest tests/ -v
```

### Production Deployment

**Option 1 - Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 2 - Direct:**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Environment Variables:**
- `GEMINI_API_KEY` (required)
- `PORT` (default 8000)

### Scaling Considerations

**Free Tier Limits:**
- 1GB storage
- 100MB per file
- Shared quota across projects

**Performance:**
- Keep stores <20GB for best latency
- Use metadata filters to narrow searches
- Consider splitting large datasets into multiple stores

**Security:**
- Never commit .env or API keys
- Use environment variables
- Validate file uploads (type, size)
- Sanitize metadata inputs

## Troubleshooting

**Common Issues:**

1. **"Operation not found" (404)**
   - Use `client.operations.get()` not `file_search_stores.get_operation()`

2. **Documents stuck in STATE_PENDING**
   - Wait 30-60s for processing
   - Large files (>10MB) may take several minutes

3. **Empty search results**
   - Verify documents are STATE_ACTIVE
   - Try broader query
   - Check metadata filters

4. **Static files 404**
   - Ensure BASE_DIR pattern used
   - Check template paths absolute

5. **SDK method errors**
   - Use `documents.list()` not `list_documents()`
   - Check correct method paths

## Additional Resources

- **Gemini API Docs:** https://ai.google.dev/gemini-api/docs/file-search
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **uv Documentation:** https://github.com/astral-sh/uv
- **Claude Code Skill:** `gemini-file-search-skill.zip` (bundled with project)

## Contributing

When adding features:

1. Follow existing patterns (singleton, tempfile, safe extraction)
2. Add tests for new endpoints
3. Update this guide with new patterns
4. Keep API routes prefixed with `/api`
5. Use absolute paths for static resources
6. Handle errors with HTTPException
7. Document new metadata filters or query options

---

**Built with:** FastAPI, Google Gemini File Search API, uv
**License:** MIT
