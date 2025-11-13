# Production Deployment

Deploy your Gemini File Search application to production.

## Deployment Checklist

Before going to production, ensure:

- [ ] API key stored securely (environment variable, not hardcoded)
- [ ] Error handling implemented for all endpoints
- [ ] Logging configured properly
- [ ] File upload size limits set
- [ ] Rate limiting added if needed
- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Documents validated before upload
- [ ] Storage limits monitored
- [ ] Backup strategy for store metadata

## Security Best Practices

### 1. Never Hardcode Secrets

**Bad:**
```python
# ❌ NEVER DO THIS
client = genai.Client(api_key='AIzaSyC...')
```

**Good:**
```python
# ✓ Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

if not os.getenv('GEMINI_API_KEY'):
    raise ValueError('GEMINI_API_KEY not set')
```

**What this code does:**
- Loads API key from .env file (not hardcoded in code)
- Creates Gemini client with environment variable
- Validates key exists before starting
- Raises error if key missing (fail fast)
- Secure: API key never appears in source code or git
- Good practice: Easy to change keys without editing code

### 2. Validate File Uploads

```python
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.xlsx', '.pptx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

async def validate_file(file: UploadFile):
    # Check extension
    ext = file.filename[file.filename.rfind('.'):].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f'File type {ext} not allowed')

    # Check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f'File too large (max 100MB)')

    await file.seek(0)  # Reset file pointer
    return content

@app.post('/upload')
async def upload(file: UploadFile):
    content = await validate_file(file)
    # Process upload...
```

**What this code does:**
- Security: Validates all uploaded files before processing
- Checks file extension (only allows safe types)
- Checks file size (rejects files >100MB)
- Prevents: Uploading malicious files, huge files that crash server
- Returns 400 error if validation fails
- Resets file pointer after reading (so can be read again)
- Critical for production: Never trust user uploads

### 3. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post('/query')
@limiter.limit('10/minute')  # Max 10 queries per minute
async def query(request: Request, query: QueryRequest):
    # Handle query...
    pass
```

**What this code does:**
- Protects against abuse: Limits requests per user/IP
- Sets up rate limiter tracking by IP address
- Decorator limits endpoint to 10 requests per minute per IP
- Exceeding limit: Returns 429 error (too many requests)
- Prevents: DOS attacks, API abuse, cost overruns
- Production essential: Protects your Gemini API quota and costs

### 4. Input Sanitization

```python
import bleach
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    question: str

    @validator('question')
    def sanitize_question(cls, v):
        # Remove HTML tags
        clean = bleach.clean(v, tags=[], strip=True)

        # Limit length
        if len(clean) > 500:
            raise ValueError('Question too long (max 500 chars)')

        return clean.strip()
```

**What this code does:**
- Sanitizes user input before processing
- Removes any HTML/script tags (prevents XSS attacks)
- Limits question length to 500 chars (prevents abuse)
- Validator runs automatically when request received
- Returns cleaned text or raises validation error
- Security: Never trust user input, always sanitize

## Deployment Options

### Option 1: Cloud Run (Google Cloud)

**Why Cloud Run:**
- Serverless (auto-scaling)
- Pay per use
- HTTPS built-in
- Easy deployment

**Setup:**

1. Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. Create `requirements.txt`:

```txt
fastapi
uvicorn[standard]
google-genai
python-multipart
python-dotenv
jinja2
```

3. Deploy:

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy document-search \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY
```

Your app is now live at: https://document-search-xxx.run.app

### Option 2: Docker + Any Cloud

**Create production Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Build and run:**

```bash
# Build
docker build -t document-search .

# Run locally
docker run -p 8000:8000 \
    -e GEMINI_API_KEY=$GEMINI_API_KEY \
    document-search

# Push to registry
docker tag document-search gcr.io/YOUR_PROJECT/document-search
docker push gcr.io/YOUR_PROJECT/document-search

# Deploy to GKE, AWS ECS, Azure Container Instances, etc.
```

### Option 3: Traditional Server (VPS)

**Setup on Ubuntu/Debian:**

```bash
# 1. Install Python
sudo apt update
sudo apt install python3.11 python3.11-venv nginx

# 2. Clone your app
git clone https://github.com/yourusername/document-search.git
cd document-search

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variables
echo "GEMINI_API_KEY=your_key" > .env

# 6. Install as systemd service
sudo nano /etc/systemd/system/document-search.service
```

**Systemd service file:**

```ini
[Unit]
Description=Document Search Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/document-search
Environment="PATH=/var/www/document-search/venv/bin"
EnvironmentFile=/var/www/document-search/.env
ExecStart=/var/www/document-search/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

**Nginx reverse proxy:**

```nginx
# /etc/nginx/sites-available/document-search
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # File upload size limit
    client_max_body_size 100M;
}
```

**Enable and start:**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/document-search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start service
sudo systemctl enable document-search
sudo systemctl start document-search

# Check status
sudo systemctl status document-search

# View logs
sudo journalctl -u document-search -f
```

**Add HTTPS with Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Configuration

### Development vs Production

**config.py:**

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    gemini_api_key: str

    # App Configuration
    environment: str = 'production'
    debug: bool = False

    # Server Configuration
    host: str = '0.0.0.0'
    port: int = 8000
    workers: int = 4

    # Upload Configuration
    max_file_size_mb: int = 100
    allowed_extensions: list = ['.pdf', '.docx', '.txt', '.md', '.xlsx']

    # Rate Limiting
    rate_limit_per_minute: int = 10

    class Config:
        env_file = '.env'

settings = Settings()
```

**main.py:**

```python
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize client
client = genai.Client(api_key=settings.gemini_api_key)

# Create app
app = FastAPI(
    title='Document Search',
    debug=settings.debug
)
```

**.env.production:**

```bash
GEMINI_API_KEY=your_production_key
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4
MAX_FILE_SIZE_MB=100
RATE_LIMIT_PER_MINUTE=10
```

## Monitoring & Logging

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        return json.dumps(log_obj)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use
@app.post('/query')
def query(request: QueryRequest):
    logger.info('Query received', extra={
        'store_id': request.store_id,
        'question_length': len(request.question)
    })

    try:
        response = client.models.generate_content(...)
        logger.info('Query successful', extra={
            'answer_length': len(response.text)
        })
        return {'answer': response.text}
    except Exception as e:
        logger.error('Query failed', extra={
            'error': str(e)
        }, exc_info=True)
        raise
```

**What this code does:**
- Structured logging in JSON format (machine-readable)
- Each log entry: timestamp, level, message, module, function
- Logs query received with metadata (store_id, question length)
- Logs success or failure with details
- JSON format: Easy to parse by log aggregation tools
- Production: Essential for debugging issues in live system
- Can search/analyze logs programmatically

### Health Check Endpoint

```python
@app.get('/health')
def health_check():
    """Health check for load balancers"""
    try:
        # Test Gemini API connection
        stores = list(client.file_search_stores.list(config={'page_size': 1}))
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'gemini_api': 'connected'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }, 503
```

**What this code does:**
- Health check endpoint for monitoring systems
- Tests Gemini API connection (list stores)
- Returns 200 + healthy if working
- Returns 503 + unhealthy if Gemini API down
- Load balancers use this to route traffic only to healthy servers
- Monitoring tools can alert if health check fails
- Critical for: Production deployments, auto-scaling, alerting

### Metrics Tracking

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Define metrics
query_counter = Counter('queries_total', 'Total queries')
query_duration = Histogram('query_duration_seconds', 'Query duration')

@app.post('/query')
def query(request: QueryRequest):
    query_counter.inc()

    with query_duration.time():
        response = client.models.generate_content(...)

    return {'answer': response.text}

@app.get('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type='text/plain')
```

## Performance Optimization

### 1. Connection Pooling

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_client():
    """Singleton client instance"""
    return genai.Client(api_key=settings.gemini_api_key)

@app.post('/query')
def query(request: QueryRequest):
    client = get_client()
    # Use client...
```

### 2. Async Operations

```python
import asyncio

@app.post('/query')
async def query(request: QueryRequest):
    loop = asyncio.get_event_loop()

    # Run blocking operation in thread pool
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(...)
    )

    return {'answer': response.text}
```

### 3. Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_query(question_hash: str, store_id: str):
    """Cache query results"""
    response = client.models.generate_content(...)
    return response.text

@app.post('/query')
def query(request: QueryRequest):
    # Hash question for cache key
    question_hash = hashlib.sha256(
        request.question.encode()
    ).hexdigest()[:16]

    answer = cached_query(question_hash, request.store_id)
    return {'answer': answer}
```

## Backup & Disaster Recovery

### Store Metadata Backup

```python
import json
from datetime import datetime

def backup_store_metadata(store_id: str):
    """Backup store and document metadata"""
    store_name = f'fileSearchStores/{store_id}'

    # Get store info
    store = client.file_search_stores.get(name=store_name)

    # Get all documents
    docs = list(client.file_search_stores.documents.list(parent=store_name))

    backup = {
        'timestamp': datetime.utcnow().isoformat(),
        'store': {
            'name': store.name,
            'display_name': store.display_name,
            'created': store.create_time,
            'documents_count': store.active_documents_count
        },
        'documents': [
            {
                'name': doc.name,
                'display_name': doc.display_name,
                'state': doc.state,
                'size': doc.size_bytes,
                'created': doc.create_time,
                'metadata': dict(doc.custom_metadata) if doc.custom_metadata else {}
            }
            for doc in docs
        ]
    }

    # Save to file
    filename = f'backup_{store_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w') as f:
        json.dump(backup, f, indent=2)

    return filename

# Schedule daily backups
@app.on_event('startup')
async def schedule_backups():
    import schedule

    def backup_all_stores():
        stores = client.file_search_stores.list()
        for store in stores:
            store_id = store.name.split('/')[-1]
            backup_store_metadata(store_id)

    schedule.every().day.at('02:00').do(backup_all_stores)
```

**What this code does:**
- Backs up store and document metadata to JSON file
- Saves: store info, document list with names/states/metadata
- Creates timestamped backup file (backup_STOREID_20250113_020000.json)
- Scheduler: Runs automatic backups daily at 2am
- Doesn't backup file contents (only metadata)
- Critical for: Disaster recovery, tracking what docs you had
- If store deleted accidentally: Can see what was in it

## Troubleshooting Production Issues

### Common Issues

**1. Out of storage:**
```python
# Monitor storage usage
def check_storage():
    stores = client.file_search_stores.list()
    total_bytes = sum(s.size_bytes for s in stores)
    total_gb = total_bytes / (1024**3)

    if total_gb > 0.9:  # 90% of 1GB free tier
        logger.warning(f'Storage nearly full: {total_gb:.2f}GB')
```

**2. Slow queries:**
```python
# Add timeout
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

@app.post('/query')
def query(request: QueryRequest):
    try:
        with timeout(30):  # 30 second timeout
            response = client.models.generate_content(...)
            return {'answer': response.text}
    except TimeoutError:
        raise HTTPException(504, 'Query timeout')
```

## Best Practices Summary

1. **Security**
   - Never hardcode secrets
   - Validate all file uploads
   - Use HTTPS in production
   - Implement rate limiting

2. **Reliability**
   - Add comprehensive error handling
   - Implement health checks
   - Monitor storage usage
   - Set up automated backups

3. **Performance**
   - Use connection pooling
   - Enable caching when appropriate
   - Set reasonable timeouts
   - Monitor query performance

4. **Operations**
   - Use structured logging (JSON)
   - Track metrics (Prometheus)
   - Set up alerts for issues
   - Document deployment process

## Next Steps

- [FastAPI Integration →](./fastapi-integration)
- [Troubleshooting →](../troubleshooting)
- [API Reference →](../api/stores)
