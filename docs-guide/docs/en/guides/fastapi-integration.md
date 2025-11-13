# FastAPI Integration

Build a web application with document search using FastAPI.

## What You'll Build

A complete web application where users can:
1. **Upload documents** through a web interface
2. **Ask questions** in natural language
3. **Get answers** with citations
4. **Manage stores** and documents

All powered by Gemini File Search.

## Why FastAPI?

**FastAPI** is perfect for building APIs because:
- Fast to write (like Flask)
- Fast to run (async support)
- Automatic API docs (Swagger UI)
- Type safety (Python type hints)
- Production-ready

## Project Setup

### Install Dependencies

```bash
# Using uv (recommended)
uv add fastapi uvicorn google-genai python-multipart python-dotenv jinja2

# Or using pip
pip install fastapi uvicorn google-genai python-multipart python-dotenv jinja2
```

### Project Structure

```
your-project/
├── main.py                 # FastAPI application
├── .env                    # Environment variables
├── templates/              # HTML templates
│   ├── index.html
│   ├── stores.html
│   └── query.html
├── static/                 # CSS, JS, images
│   ├── style.css
│   └── app.js
└── requirements.txt        # Dependencies
```

## Basic FastAPI Application

### Minimal Example

```python
# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from google import genai

load_dotenv()

app = FastAPI(title='Document Search')

# Initialize Gemini client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

@app.get('/')
def home():
    return {'message': 'Document Search API'}

@app.get('/stores')
def list_stores():
    """List all file search stores"""
    stores = client.file_search_stores.list(config={'page_size': 20})
    return {
        'stores': [
            {
                'name': store.name,
                'display_name': store.display_name,
                'documents': store.active_documents_count
            }
            for store in stores
        ]
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
```

**What this code does:**
- Creates FastAPI web application for document search
- Loads API key from environment (secure)
- Initializes Gemini client once at startup
- Home endpoint (/): Returns simple welcome message
- Stores endpoint (/stores): Lists all your document stores with names and doc counts
- Main block: Runs web server on localhost port 8000
- Result: RESTful API for accessing your document search

Run it:
```bash
python main.py
```

Visit http://127.0.0.1:8000/stores

## Complete API Endpoints

### Create Store

```python
from fastapi import HTTPException
from pydantic import BaseModel

class CreateStoreRequest(BaseModel):
    display_name: str

@app.post('/stores')
def create_store(request: CreateStoreRequest):
    """Create a new file search store"""
    try:
        store = client.file_search_stores.create(
            config={'display_name': request.display_name}
        )
        return {
            'name': store.name,
            'display_name': store.display_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**What this code does:**
- Defines request model: requires display_name field
- POST /stores endpoint: Creates new document store
- Takes store name from request body (JSON)
- Creates store via Gemini API
- Returns store ID and name in response
- Error handling: Returns 500 error if creation fails
- Think: "Create new library" endpoint

### Upload Document

```python
from fastapi import File, UploadFile, Form
import tempfile
import time

@app.post('/stores/{store_id}/documents')
async def upload_document(
    store_id: str,
    file: UploadFile = File(...),
    display_name: str = Form(None)
):
    """Upload document to store"""
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{file.filename}') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Upload to Gemini
        operation = client.file_search_stores.upload_to_file_search_store(
            file=tmp_path,
            file_search_store_name=f'fileSearchStores/{store_id}',
            config={'display_name': display_name or file.filename}
        )

        # Wait for processing
        max_wait = 60  # seconds
        start = time.time()
        while not operation.done and (time.time() - start) < max_wait:
            operation = client.operations.get(name=operation.name)
            time.sleep(2)

        if not operation.done:
            raise HTTPException(status_code=408, detail='Upload timeout')

        doc = operation.response.document

        return {
            'document_name': doc.name,
            'display_name': doc.display_name,
            'state': doc.state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
```

**What this code does:**
- POST /stores/{store_id}/documents endpoint: Upload file to specific store
- Accepts file upload (multipart/form-data) from web browser/client
- Saves uploaded file temporarily to disk
- Uploads temp file to Gemini store
- Waits up to 60 seconds for processing (polls every 2 seconds)
- Returns document info (name, state) when done
- Cleanup: Deletes temp file after upload (even if error)
- Timeout protection: Returns 408 if processing takes too long

### Query Documents

```python
from google.genai import types

class QueryRequest(BaseModel):
    question: str
    store_id: str
    metadata_filter: str = None

@app.post('/query')
def query_documents(request: QueryRequest):
    """Query documents in a store"""
    try:
        store_name = f'fileSearchStores/{request.store_id}'

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.question,
            config=types.GenerateContentConfig(
                tools=[types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name],
                        metadata_filter=request.metadata_filter
                    )
                )]
            )
        )

        # Extract citations
        citations = []
        for candidate in response.candidates:
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                for chunk in candidate.grounding_metadata.grounding_chunks:
                    citations.append({
                        'document': chunk.document_name.split('/')[-1] if hasattr(chunk, 'document_name') else 'Unknown',
                        'relevance': getattr(chunk, 'relevance_score', 0)
                    })

        return {
            'answer': response.text,
            'citations': citations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**What this code does:**
- POST /query endpoint: Ask questions and get answers
- Request model: question, store_id, optional metadata_filter
- Builds store name from store_id
- Queries Gemini with file search enabled
- Extracts citations from response (document names + relevance scores)
- Returns JSON with answer text and list of source citations
- Error handling: Returns 500 if query fails
- Think: Main "ask a question" endpoint for your app

### List Documents

```python
@app.get('/stores/{store_id}/documents')
def list_documents(store_id: str):
    """List all documents in a store"""
    try:
        store_name = f'fileSearchStores/{store_id}'
        docs = client.file_search_stores.documents.list(parent=store_name)

        return {
            'documents': [
                {
                    'name': doc.name.split('/')[-1],
                    'display_name': doc.display_name,
                    'state': doc.state,
                    'size_bytes': doc.size_bytes,
                    'created': doc.create_time
                }
                for doc in docs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**What this code does:**
- GET /stores/{store_id}/documents endpoint: List all docs in store
- Takes store_id from URL path
- Fetches all documents from that store
- Returns list with doc info: name, display name, state, size, creation time
- Good for: Showing user what documents are in their store
- Error handling: Returns 500 if listing fails

### Delete Store

```python
@app.delete('/stores/{store_id}')
def delete_store(store_id: str, force: bool = False):
    """Delete a store"""
    try:
        store_name = f'fileSearchStores/{store_id}'
        client.file_search_stores.delete(
            name=store_name,
            config={'force': force}
        )
        return {'message': 'Store deleted'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**What this code does:**
- DELETE /stores/{store_id} endpoint: Delete a store
- Takes store_id from URL, optional force parameter
- force=True: Delete even if store has documents
- force=False (default): Only delete if empty
- Calls Gemini API to delete store
- Returns success message
- Warning: Permanent deletion, use with caution

## Adding a Web Interface

### HTML Template

Create `templates/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Document Search</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>Document Search</h1>

        <!-- Upload Section -->
        <div class="section">
            <h2>Upload Document</h2>
            <form id="upload-form">
                <select id="store-select" required>
                    <option value="">Select Store</option>
                </select>
                <input type="file" id="file-input" required>
                <button type="submit">Upload</button>
            </form>
            <div id="upload-status"></div>
        </div>

        <!-- Query Section -->
        <div class="section">
            <h2>Ask a Question</h2>
            <form id="query-form">
                <select id="query-store-select" required>
                    <option value="">Select Store</option>
                </select>
                <input type="text" id="question-input" placeholder="What was Q2 revenue?" required>
                <button type="submit">Search</button>
            </form>
            <div id="answer-box"></div>
        </div>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>
```

### Serve Templates

```python
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request
from pathlib import Path

# Setup templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

@app.get('/', response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
```

**What this code does:**
- Sets up web interface (HTML templates + static files)
- BASE_DIR: Gets directory where main.py lives
- Templates: Loads HTML files from templates/ folder
- Static files: Serves CSS, JS, images from static/ folder
- Home page endpoint: Returns rendered HTML template
- Turns API into full web application with UI
- Users can upload/query through browser instead of API calls

### JavaScript for Interactivity

Create `static/app.js`:

```javascript
// Load stores on page load
async function loadStores() {
    const response = await fetch('/stores');
    const data = await response.json();

    const storeSelects = document.querySelectorAll('#store-select, #query-store-select');
    storeSelects.forEach(select => {
        select.innerHTML = '<option value="">Select Store</option>';
        data.stores.forEach(store => {
            const option = document.createElement('option');
            option.value = store.name.split('/')[1];
            option.textContent = `${store.display_name} (${store.documents} docs)`;
            select.appendChild(option);
        });
    });
}

// Upload document
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const storeId = document.getElementById('store-select').value;
    const fileInput = document.getElementById('file-input');
    const statusDiv = document.getElementById('upload-status');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    statusDiv.textContent = 'Uploading...';

    try {
        const response = await fetch(`/stores/${storeId}/documents`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            statusDiv.textContent = '✓ Upload complete!';
            fileInput.value = '';
        } else {
            statusDiv.textContent = '✗ Upload failed';
        }
    } catch (error) {
        statusDiv.textContent = `✗ Error: ${error}`;
    }
});

// Query documents
document.getElementById('query-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const storeId = document.getElementById('query-store-select').value;
    const question = document.getElementById('question-input').value;
    const answerBox = document.getElementById('answer-box');

    answerBox.innerHTML = '<div class="loading">Searching...</div>';

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question: question,
                store_id: storeId
            })
        });

        const data = await response.json();

        // Display answer
        answerBox.innerHTML = `
            <div class="answer">
                <h3>Answer:</h3>
                <p>${data.answer}</p>
                <h4>Sources:</h4>
                <ul>
                    ${data.citations.map(c => `<li>${c.document} (${c.relevance.toFixed(2)})</li>`).join('')}
                </ul>
            </div>
        `;
    } catch (error) {
        answerBox.innerHTML = `<div class="error">Error: ${error}</div>`;
    }
});

// Load stores on page load
loadStores();
```

### Basic CSS

Create `static/style.css`:

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
    color: #333;
    margin-bottom: 30px;
}

.section {
    margin-bottom: 40px;
}

h2 {
    color: #555;
    margin-bottom: 15px;
    font-size: 18px;
}

form {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

select, input[type="text"], input[type="file"] {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

button {
    padding: 10px 20px;
    background: #4285f4;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background: #357ae8;
}

#upload-status {
    padding: 10px;
    border-radius: 4px;
    font-size: 14px;
}

.answer {
    padding: 20px;
    background: #f9f9f9;
    border-radius: 4px;
    border-left: 4px solid #4285f4;
}

.answer h3 {
    color: #333;
    margin-bottom: 10px;
}

.answer p {
    line-height: 1.6;
    margin-bottom: 15px;
}

.answer ul {
    list-style: none;
    padding: 0;
}

.answer li {
    padding: 5px 0;
    color: #666;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #666;
}

.error {
    padding: 15px;
    background: #fee;
    color: #c33;
    border-radius: 4px;
}
```

## Running the Application

### Development Mode

```bash
# Using uv
uv run uvicorn main:app --reload

# Or using uvicorn directly
uvicorn main:app --reload
```

Visit http://127.0.0.1:8000

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Error Handling

### Comprehensive Error Handling

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions"""
    return JSONResponse(
        status_code=500,
        content={'error': str(exc)}
    )

# Specific error handling
@app.post('/query')
def query_documents(request: QueryRequest):
    # Validate store exists
    try:
        store_name = f'fileSearchStores/{request.store_id}'
        client.file_search_stores.get(name=store_name)
    except:
        raise HTTPException(status_code=404, detail='Store not found')

    # Validate documents exist
    docs = list(client.file_search_stores.documents.list(parent=store_name))
    if not docs:
        raise HTTPException(status_code=400, detail='Store has no documents')

    # Check if documents are active
    active_docs = [d for d in docs if d.state == 'STATE_ACTIVE']
    if not active_docs:
        raise HTTPException(status_code=400, detail='No active documents in store')

    # Query
    try:
        response = client.models.generate_content(...)
        return {'answer': response.text, 'citations': [...]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Query failed: {str(e)}')
```

## Best Practices

### 1. Environment Variables

Never hardcode API keys:

```python
# .env
GEMINI_API_KEY=your_api_key_here
PORT=8000
HOST=127.0.0.1

# main.py
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError('GEMINI_API_KEY not set')
```

### 2. Async Operations

Use async for better performance:

```python
import asyncio

@app.post('/stores/{store_id}/documents')
async def upload_document(store_id: str, file: UploadFile = File(...)):
    # Async file operations
    content = await file.read()

    # Run blocking Gemini calls in thread pool
    loop = asyncio.get_event_loop()
    operation = await loop.run_in_executor(
        None,
        lambda: client.file_search_stores.upload_to_file_search_store(...)
    )

    return {'status': 'uploaded'}
```

### 3. Request Validation

Use Pydantic models:

```python
from pydantic import BaseModel, Field, validator

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    store_id: str
    metadata_filter: str = None

    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
```

### 4. Logging

Add proper logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post('/query')
def query_documents(request: QueryRequest):
    logger.info(f'Query: {request.question} (store: {request.store_id})')

    try:
        response = client.models.generate_content(...)
        logger.info(f'Query successful, answer length: {len(response.text)}')
        return {'answer': response.text}
    except Exception as e:
        logger.error(f'Query failed: {str(e)}')
        raise
```

## Next Steps

- [Production Deployment →](./production-deployment)
- [API Reference →](../api/query)
- [Troubleshooting →](../troubleshooting)
