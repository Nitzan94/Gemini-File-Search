# Uploading Documents

Complete guide to uploading files to your stores.

## The Upload Process

Think of uploading like sending books to a library where a librarian will:
1. **Receive the book** (upload file)
2. **Catalog it** (process and chunk)
3. **Index it** (generate embeddings)
4. **Shelve it** (make searchable)

This all happens automatically - you just upload, wait a bit, then search.

## Basic Upload

### Simplest Example

```python
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Upload to existing store
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name='fileSearchStores/your-store-id'
)
```

That's it! The file is now uploading and processing.

### With Custom Name

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='Q2_Final_Report_v3.pdf',
    file_search_store_name=store.name,
    config={
        'display_name': 'Q2 2024 Financial Report'  # Cleaner name
    }
)
```

## Understanding the Upload Flow

```mermaid
sequenceDiagram
    participant You
    participant API as Gemini API
    participant Store as File Search Store
    participant AI as Processing

    You->>API: Upload file
    API->>Store: Store file
    API-->>You: Operation ID

    Note over AI: Background Processing

    AI->>Store: Split into chunks
    AI->>Store: Generate embeddings
    AI->>Store: Build search index

    You->>API: Check status
    API-->>You: STATE_ACTIVE ✓

    You->>API: Query
    API->>Store: Search
    Store-->>API: Relevant chunks
    API-->>You: Answer + Citations
```

### What Happens Behind the Scenes

When you upload a 100-page PDF:

1. **File Received** (seconds)
   - File uploaded to Google's servers
   - Basic validation (format, size)
   - Operation ID returned to you

2. **Document Processing** (30-60 seconds)
   - Text extraction from PDF
   - Splitting into meaningful chunks
   - Each chunk analyzed for meaning

3. **Embedding Generation** (30-60 seconds)
   - Each chunk converted to mathematical representation
   - Embeddings enable semantic search
   - All handled by Google automatically

4. **Indexing** (seconds)
   - Embeddings stored in vector database
   - Search index built
   - Document marked as STATE_ACTIVE

**Total time:** 1-2 minutes for typical documents

## Waiting for Processing

You MUST wait for documents to be processed before querying.

### The Right Way - Poll Until Active

```python
import time

operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name=store.name,
    config={'display_name': 'My Report'}
)

print('Uploading and processing...')

# Wait for operation to complete
while not operation.done:
    operation = client.operations.get(name=operation.name)
    print(f'Status: Processing...')
    time.sleep(2)

print('Upload complete! Document is ready.')
```

### The Wrong Way - Don't Do This

```python
# BAD: Immediate query
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name=store.name
)

# This will fail or return empty results!
response = client.models.generate_content(...)  # ❌ Too soon!
```

### Check Document State

After upload completes, verify the document is active:

```python
# Get document from operation result
doc_name = operation.response.document.name

# Check state
doc = client.file_search_stores.documents.get(name=doc_name)

if doc.state == 'STATE_ACTIVE':
    print('✓ Ready to query')
elif doc.state == 'STATE_PENDING':
    print('⏳ Still processing, wait longer')
elif doc.state == 'STATE_FAILED':
    print('✗ Processing failed, check document')
```

## Uploading Multiple Files

### Sequential Upload (Simple)

```python
files = ['report1.pdf', 'report2.pdf', 'report3.pdf']

for file in files:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=file,
        file_search_store_name=store.name,
        config={'display_name': file.replace('.pdf', '')}
    )

    # Wait for this file to complete
    while not operation.done:
        operation = client.operations.get(name=operation.name)
        time.sleep(2)

    print(f'✓ {file} uploaded')
```

### Parallel Upload (Faster)

```python
import concurrent.futures

def upload_file(filepath, store_name):
    operation = client.file_search_stores.upload_to_file_search_store(
        file=filepath,
        file_search_store_name=store_name,
        config={'display_name': filepath.split('/')[-1]}
    )

    # Wait for completion
    while not operation.done:
        operation = client.operations.get(name=operation.name)
        time.sleep(2)

    return filepath

files = ['report1.pdf', 'report2.pdf', 'report3.pdf']

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(upload_file, f, store.name) for f in files]

    for future in concurrent.futures.as_completed(futures):
        print(f'✓ {future.result()} uploaded')
```

## Adding Metadata

Metadata makes documents searchable by category, date, author, etc.

### Basic Metadata

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name=store.name,
    config={
        'display_name': 'Q2 Financial Report',
        'custom_metadata': [
            {'key': 'department', 'string_value': 'Finance'},
            {'key': 'year', 'string_value': '2024'},
            {'key': 'quarter', 'string_value': 'Q2'},
            {'key': 'confidential', 'string_value': 'yes'}
        ]
    }
)
```

### Why Metadata Matters

**Without metadata:**
You upload 100 documents. To find Q2 financial reports, you must:
1. Query all 100 documents
2. Hope semantic search finds the right ones
3. Manually filter results

**With metadata:**
```python
# Query only Q2 financial documents
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What was total revenue?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='quarter=Q2 AND department=Finance'
            )
        )]
    )
)
```

Searches only relevant documents - faster and more accurate.

### Metadata Best Practices

**Good metadata keys:**
- `department` - Finance, Engineering, HR
- `year` - 2024, 2023
- `quarter` - Q1, Q2, Q3, Q4
- `category` - financial, technical, legal
- `author` - person or team name
- `status` - draft, final, archived
- `project` - project name or ID

**Max 20 key-value pairs per document**

## Uploading Different File Types

### PDFs (Most Common)

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='annual_report.pdf',
    file_search_store_name=store.name,
    config={'display_name': 'Annual Report 2024'}
)
```

Works with:
- Text-based PDFs ✓
- Scanned PDFs with embedded text ✓
- Image-only PDFs (limited OCR) ⚠️

### Word Documents

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='policy.docx',
    file_search_store_name=store.name
)
```

Supports: .docx, .doc

### Excel Spreadsheets

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='sales_data.xlsx',
    file_search_store_name=store.name
)
```

Extracts:
- Sheet names
- Cell values
- Column headers

Best for: Reports with text descriptions, not pure number tables

### Code Files

```python
files = ['main.py', 'utils.js', 'README.md']

for file in files:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=file,
        file_search_store_name=store.name
    )
```

Great for:
- Code documentation
- Finding specific functions
- Understanding architecture

### Text Files

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='meeting_notes.txt',
    file_search_store_name=store.name
)
```

Supports: .txt, .md, .rtf

### ZIP Archives (Auto-Extracted)

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='project_docs.zip',
    file_search_store_name=store.name
)
```

Automatically:
- Extracts all files
- Uploads each individually
- Preserves folder structure in names

Perfect for: Bulk uploading entire document sets

## File Size and Limits

| What | Limit |
|------|-------|
| Max file size | 100 MB |
| Total storage (free tier) | 1 GB |
| Recommended file size | < 10 MB for fast processing |
| Processing time (1 MB) | ~30-60 seconds |
| Processing time (10 MB) | ~2-3 minutes |
| Processing time (100 MB) | ~5-10 minutes |

### If Your File is Too Large

**Option 1: Split the PDF**

```bash
# Using PyPDF2
pip install PyPDF2

python split_pdf.py large_file.pdf
# Creates: page_1.pdf, page_2.pdf, ...
```

**Option 2: Compress the PDF**

Use online tools or:
```bash
# Using Ghostscript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET \
   -dBATCH -sOutputFile=compressed.pdf input.pdf
```

**Option 3: Extract text only**

```python
# Upload as plain text instead
import PyPDF2

with open('large.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = '\n'.join(page.extract_text() for page in reader.pages)

with open('extracted.txt', 'w') as f:
    f.write(text)

# Upload text file (much smaller)
operation = client.file_search_stores.upload_to_file_search_store(
    file='extracted.txt',
    file_search_store_name=store.name
)
```

## Troubleshooting Uploads

### Upload Hangs

**Cause:** Network timeout or large file

**Solution:**
- Check internet connection
- Try smaller file
- Increase timeout in code

### STATE_FAILED After Upload

**Possible causes:**
1. **Unsupported format** - Check file extension
2. **Corrupted file** - Try opening file locally first
3. **Empty file** - Verify file has content
4. **Encoding issues** - Use UTF-8 for text files

**Check error:**
```python
doc = client.file_search_stores.documents.get(name=doc_name)
if doc.state == 'STATE_FAILED':
    print(f'Failed: {doc}')  # Check for error details
```

### Document Not Found After Upload

**Cause:** Querying before processing complete

**Solution:** Always poll operation until `done=True`

### Slow Processing

**Cause:** Large file or peak usage times

**Solution:**
- Be patient (large files take time)
- Upload during off-peak hours
- Consider splitting large files

## Best Practices

1. **Use descriptive display names** - "Q2 Report" not "document_final_v3.pdf"
2. **Add metadata** - Makes filtering faster and more accurate
3. **Wait for STATE_ACTIVE** - Never query before processing completes
4. **Upload in batches** - Parallel upload for multiple files
5. **Compress large files** - Faster upload and processing
6. **Use UTF-8 encoding** - For text files to avoid encoding errors
7. **Verify formats** - Check supported formats before uploading
8. **Monitor storage** - Track usage against tier limits
9. **Clean up** - Delete old/unused documents regularly

## Next Steps

- [Query Your Documents →](./query)
- [Metadata Filtering →](./metadata-filtering)
- [Document States →](../concepts/documents)
- [Production Deployment →](./production-deployment)
