# Troubleshooting

Common issues and solutions.

## API Connection

### Error: "GEMINI_API_KEY not found"

**Solution:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_key" > .env

# Verify
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

### Error: "Invalid API key"

**Solutions:**
1. Get new key: https://aistudio.google.com/apikey
2. Update `.env` file
3. Restart application

### Error: "Module 'google.genai' not found"

**Solution:**
```bash
pip install google-genai
```

## Storage & Upload

### Error: "Storage limit exceeded"

**Cause:** Free tier 1GB limit reached

**Solution:**
```python
# Check usage
stores = client.file_search_stores.list()
total = sum(s.size_bytes for s in stores)
print(f'{total / 1024 / 1024:.2f} MB used')

# Delete unused stores
client.file_search_stores.delete(name='...', config={'force': True})
```

### Error: "File too large"

**Cause:** File exceeds 100MB limit

**Solution:**
- Split large files
- Compress before upload
- Use PDF optimization tools

### Upload hangs or times out

**Solution:**
```python
# Increase timeout
import time
max_attempts = 30
while not operation.done and attempts < max_attempts:
    operation = client.operations.get(name=operation.name)
    time.sleep(2)
    attempts += 1
```

## Document Processing

### Documents stuck in "STATE_PENDING"

**Cause:** Background processing not complete

**Solution:**
- Wait 30-60 seconds for small files
- Large files (>10MB) may take several minutes
- Check operation status:

```python
operation = client.operations.get(name=operation_name)
print(f'Done: {operation.done}')
```

### Error: "Document not found" after upload

**Cause:** Querying before processing complete

**Solution:**
```python
def wait_for_document(client, doc_name, timeout=60):
    import time
    start = time.time()
    while time.time() - start < timeout:
        doc = client.file_search_stores.documents.get(name=doc_name)
        if doc.state == 'STATE_ACTIVE':
            return doc
        time.sleep(2)
    raise TimeoutError('Document processing timeout')
```

### Documents in "STATE_FAILED"

**Causes:**
- Unsupported format
- Corrupted file
- Encoding issues

**Solution:**
1. Check format is supported (PDF, DOCX, etc.)
2. Verify file not corrupted
3. Try re-uploading
4. Use UTF-8 encoding for text

## Query Issues

### Empty or generic answers

**Cause:** Document not processed or query too broad

**Solution:**
```python
# Check document state
docs = client.file_search_stores.documents.list(parent=store_name)
for doc in docs:
    print(f'{doc.display_name}: {doc.state}')  # Should be STATE_ACTIVE

# Make query more specific
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='According to the Q2 report, what was the exact revenue figure?',
    # ...
)
```

### No citations

**Cause:** Answer from model knowledge, not documents

**Solution:**
- Make query more specific to document content
- Verify document uploaded successfully
- Check if document contains relevant info

### Query timeout

**Cause:** Large store or complex query

**Solution:**
```python
# Use metadata filters to narrow search
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=query,
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='year=2024'  # Narrow scope
            )
        )]
    )
)
```

## SDK Method Errors

### Error: "'FileSearchStores' object has no attribute 'list_documents'"

**Cause:** Wrong SDK method path

**Solution:**
```python
# Correct: documents is a sub-resource
documents = client.file_search_stores.documents.list(
    parent='fileSearchStores/store-id'
)

# NOT: client.file_search_stores.list_documents()
```

### Error: "Operation not found" (404)

**Cause:** Wrong operation endpoint

**Solution:**
```python
# Correct method
operation = client.operations.get(name=operation_name)

# NOT: client.file_search_stores.get_operation()

# Full operation name includes path:
# 'fileSearchStores/store-id/upload/operations/op-id'
```

## FastAPI Integration

### Static files return 404

**Cause:** Relative paths don't work with uvicorn

**Solution:**
```python
from pathlib import Path

BASE_DIR = Path(__file__).parent
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')))
```

### Route conflicts

**Cause:** API and page routes use same path

**Solution:**
```python
# Prefix API routes
router = APIRouter(prefix='/api/stores')

# Page routes separate
@app.get('/stores/{store_id}')  # HTML page
```

### Multipart upload fails

**Cause:** Missing `python-multipart` dependency

**Solution:**
```bash
pip install python-multipart
```

## Performance

### Slow queries

**Cause:** Large store (>20GB) or many documents

**Solution:**
- Keep stores <20GB for best latency
- Use metadata filters
- Split into multiple smaller stores
- Upgrade to Pro model

### High memory usage

**Cause:** Loading large files

**Solution:**
```python
# Stream file uploads
with tempfile.NamedTemporaryFile(delete=False) as tmp:
    while chunk := await file.read(8192):
        tmp.write(chunk)
```

## Debug Checklist

When troubleshooting, check in order:

1. ✓ API key valid and loaded
2. ✓ SDK installed and correct version
3. ✓ Documents in STATE_ACTIVE (not pending)
4. ✓ Store ID format correct (`fileSearchStores/...`)
5. ✓ File size under 100MB
6. ✓ File format supported
7. ✓ Storage under tier limit
8. ✓ Network connection stable
9. ✓ Correct SDK method paths
10. ✓ Citations extracted safely

## Getting Help

- [Official Docs](https://ai.google.dev/gemini-api/docs/file-search)
- [SDK Version](https://github.com/googleapis/python-genai)
- [Test Connection](./getting-started/setup#test-your-connection)
- [API Status](https://status.cloud.google.com/)
