# Documents API Reference

Complete reference for working with documents in file search stores.

## Document Resource

A document is a file uploaded to a store that has been processed for semantic search.

### Document Properties

```python
doc = client.file_search_stores.documents.get(
    name='fileSearchStores/store-id/documents/doc-id'
)

# Properties
doc.name                # str: 'fileSearchStores/.../documents/doc-id'
doc.display_name        # str: 'Q2 Financial Report'
doc.state              # str: 'STATE_ACTIVE' | 'STATE_PENDING' | 'STATE_FAILED'
doc.size_bytes         # int: 1048576 (1 MB)
doc.mime_type          # str: 'application/pdf'
doc.create_time        # str: '2024-11-13T10:30:00Z'
doc.update_time        # str: '2024-11-13T10:35:00Z'
doc.custom_metadata    # list[dict]: [{'key': 'year', 'string_value': '2024'}, ...]
```

## Document States

### STATE_PENDING

Document is being processed:
- Text extraction in progress
- Chunking and embedding generation
- Typically 30-60 seconds for small files

**Cannot query yet** - wait for STATE_ACTIVE.

### STATE_ACTIVE

Document is ready:
- All processing complete
- Fully searchable
- Can be queried

### STATE_FAILED

Processing failed:
- Unsupported format
- Corrupted file
- Encoding issues

Check file and re-upload.

## Methods

### list()

List all documents in a store.

**Signature:**
```python
client.file_search_stores.documents.list(
    parent: str,
    config: dict = None
) -> Iterator[Document]
```

**Parameters:**
- `parent` (str, required): Store resource name (`fileSearchStores/store-id`)
- `config` (dict, optional): Configuration options
  - `page_size` (int, optional): Documents per page (default: 10, max: 100)

**Returns:**
- Iterator of `Document` objects

**Basic example:**
```python
# List all documents
docs = client.file_search_stores.documents.list(
    parent='fileSearchStores/abc123'
)

for doc in docs:
    print(f'{doc.display_name}: {doc.state}')
```

**With pagination:**
```python
docs = client.file_search_stores.documents.list(
    parent='fileSearchStores/abc123',
    config={'page_size': 20}
)

for doc in docs:
    size_mb = doc.size_bytes / (1024 * 1024)
    print(f'{doc.display_name} ({size_mb:.2f} MB) - {doc.state}')
```

**Filter by state:**
```python
docs = client.file_search_stores.documents.list(parent=store.name)

active_docs = [d for d in docs if d.state == 'STATE_ACTIVE']
pending_docs = [d for d in docs if d.state == 'STATE_PENDING']
failed_docs = [d for d in docs if d.state == 'STATE_FAILED']

print(f'Active: {len(active_docs)}')
print(f'Pending: {len(pending_docs)}')
print(f'Failed: {len(failed_docs)}')
```

---

### get()

Get a specific document by name.

**Signature:**
```python
client.file_search_stores.documents.get(
    name: str
) -> Document
```

**Parameters:**
- `name` (str, required): Full document resource name

**Returns:**
- `Document` object

**Raises:**
- `NotFoundError`: Document does not exist

**Example:**
```python
doc = client.file_search_stores.documents.get(
    name='fileSearchStores/abc123/documents/doc456'
)

print(f'Name: {doc.display_name}')
print(f'State: {doc.state}')
print(f'Size: {doc.size_bytes} bytes')
print(f'Type: {doc.mime_type}')
```

**Check if document is ready:**
```python
def is_document_ready(doc_name):
    doc = client.file_search_stores.documents.get(name=doc_name)
    return doc.state == 'STATE_ACTIVE'

if is_document_ready('fileSearchStores/abc123/documents/doc456'):
    print('Ready to query!')
else:
    print('Still processing...')
```

**Error handling:**
```python
try:
    doc = client.file_search_stores.documents.get(name='fileSearchStores/.../invalid')
except Exception as e:
    print(f'Document not found: {e}')
```

---

### delete()

Delete a document from a store.

**Signature:**
```python
client.file_search_stores.documents.delete(
    name: str
) -> None
```

**Parameters:**
- `name` (str, required): Full document resource name

**Returns:**
- None

**Raises:**
- `NotFoundError`: Document does not exist

**Example:**
```python
client.file_search_stores.documents.delete(
    name='fileSearchStores/abc123/documents/doc456'
)
print('Document deleted')
```

**Safe deletion:**
```python
def safe_delete_document(doc_name):
    """Delete document with confirmation"""
    try:
        doc = client.file_search_stores.documents.get(name=doc_name)
        print(f'Delete "{doc.display_name}"?')
        confirm = input('yes/no: ')

        if confirm.lower() == 'yes':
            client.file_search_stores.documents.delete(name=doc_name)
            print('Deleted')
        else:
            print('Cancelled')
    except Exception as e:
        print(f'Error: {e}')

safe_delete_document('fileSearchStores/abc123/documents/doc456')
```

**Bulk deletion:**
```python
def delete_failed_documents(store_name):
    """Delete all failed documents in a store"""
    docs = client.file_search_stores.documents.list(parent=store_name)
    failed = [d for d in docs if d.state == 'STATE_FAILED']

    for doc in failed:
        print(f'Deleting failed document: {doc.display_name}')
        client.file_search_stores.documents.delete(name=doc.name)

    print(f'Deleted {len(failed)} failed documents')

delete_failed_documents('fileSearchStores/abc123')
```

## Working with Custom Metadata

### Metadata Structure

Metadata is a list of key-value pairs:

```python
custom_metadata = [
    {'key': 'department', 'string_value': 'Finance'},
    {'key': 'year', 'string_value': '2024'},
    {'key': 'quarter', 'string_value': 'Q2'}
]
```

### Reading Metadata

```python
doc = client.file_search_stores.documents.get(name=doc_name)

if doc.custom_metadata:
    print('Metadata:')
    for item in doc.custom_metadata:
        print(f'  {item.key}: {item.string_value}')
else:
    print('No metadata')
```

### Metadata Constraints

- **Max 20 key-value pairs** per document
- **Keys**: Must be valid identifiers (letters, numbers, underscores)
- **Values**: Strings only
- **Case-sensitive**: `Department` ≠ `department`

### Extract as Dictionary

```python
def get_metadata_dict(doc):
    """Convert metadata list to dictionary"""
    if not doc.custom_metadata:
        return {}

    return {
        item.key: item.string_value
        for item in doc.custom_metadata
    }

doc = client.file_search_stores.documents.get(name=doc_name)
metadata = get_metadata_dict(doc)

print(metadata)
# {'department': 'Finance', 'year': '2024', 'quarter': 'Q2'}
```

## Complete Examples

### Wait for Document Processing

```python
import time

def wait_for_document(doc_name, timeout=60):
    """Wait for document to become active"""
    start = time.time()

    while (time.time() - start) < timeout:
        doc = client.file_search_stores.documents.get(name=doc_name)

        if doc.state == 'STATE_ACTIVE':
            print(f'✓ {doc.display_name} is ready')
            return doc
        elif doc.state == 'STATE_FAILED':
            raise Exception(f'Document processing failed: {doc.display_name}')

        print(f'⏳ {doc.display_name} still processing...')
        time.sleep(2)

    raise TimeoutError(f'Document processing timeout after {timeout}s')

# Use it
operation = client.file_search_stores.upload_to_file_search_store(...)

# Wait for operation
while not operation.done:
    operation = client.operations.get(name=operation.name)
    time.sleep(2)

# Wait for document to be active
doc = wait_for_document(operation.response.document.name)
```

### List Documents with Metadata

```python
def list_documents_with_metadata(store_name):
    """Display all documents with their metadata"""
    docs = client.file_search_stores.documents.list(parent=store_name)

    for doc in docs:
        print(f'\n{doc.display_name}')
        print(f'  State: {doc.state}')
        print(f'  Size: {doc.size_bytes / 1024:.2f} KB')
        print(f'  Created: {doc.create_time}')

        if doc.custom_metadata:
            print('  Metadata:')
            for item in doc.custom_metadata:
                print(f'    {item.key}: {item.string_value}')
        else:
            print('  Metadata: None')

list_documents_with_metadata('fileSearchStores/abc123')
```

### Filter Documents by Metadata

```python
def find_documents_by_metadata(store_name, key, value):
    """Find documents matching specific metadata"""
    docs = client.file_search_stores.documents.list(parent=store_name)
    matches = []

    for doc in docs:
        if not doc.custom_metadata:
            continue

        for item in doc.custom_metadata:
            if item.key == key and item.string_value == value:
                matches.append(doc)
                break

    return matches

# Find all Finance documents
finance_docs = find_documents_by_metadata(
    store_name='fileSearchStores/abc123',
    key='department',
    value='Finance'
)

print(f'Found {len(finance_docs)} Finance documents')
for doc in finance_docs:
    print(f'  - {doc.display_name}')
```

### Monitor Document Processing

```python
def monitor_pending_documents(store_name):
    """Show progress of pending documents"""
    while True:
        docs = list(client.file_search_stores.documents.list(parent=store_name))

        pending = [d for d in docs if d.state == 'STATE_PENDING']
        active = [d for d in docs if d.state == 'STATE_ACTIVE']
        failed = [d for d in docs if d.state == 'STATE_FAILED']

        print(f'\rActive: {len(active)} | Pending: {len(pending)} | Failed: {len(failed)}', end='')

        if not pending:
            print('\n✓ All documents processed!')
            break

        time.sleep(2)

# Upload multiple files
for file in files:
    client.file_search_stores.upload_to_file_search_store(
        file=file,
        file_search_store_name=store.name
    )

# Monitor progress
monitor_pending_documents(store.name)
```

### Calculate Store Statistics

```python
def store_statistics(store_name):
    """Calculate detailed store statistics"""
    docs = list(client.file_search_stores.documents.list(parent=store_name))

    total_size = sum(d.size_bytes for d in docs)
    active = [d for d in docs if d.state == 'STATE_ACTIVE']
    pending = [d for d in docs if d.state == 'STATE_PENDING']
    failed = [d for d in docs if d.state == 'STATE_FAILED']

    # Count by mime type
    mime_types = {}
    for doc in docs:
        mime = doc.mime_type
        mime_types[mime] = mime_types.get(mime, 0) + 1

    # Count by metadata
    departments = {}
    for doc in docs:
        if doc.custom_metadata:
            for item in doc.custom_metadata:
                if item.key == 'department':
                    dept = item.string_value
                    departments[dept] = departments.get(dept, 0) + 1

    print(f'Store Statistics')
    print(f'================')
    print(f'Total documents: {len(docs)}')
    print(f'  Active: {len(active)}')
    print(f'  Pending: {len(pending)}')
    print(f'  Failed: {len(failed)}')
    print(f'Total size: {total_size / (1024 * 1024):.2f} MB')
    print(f'\nFile types:')
    for mime, count in sorted(mime_types.items()):
        print(f'  {mime}: {count}')
    print(f'\nDepartments:')
    for dept, count in sorted(departments.items()):
        print(f'  {dept}: {count}')

store_statistics('fileSearchStores/abc123')
```

### Clean Up Old Documents

```python
from datetime import datetime, timedelta

def delete_old_documents(store_name, days_old=90):
    """Delete documents older than specified days"""
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    docs = client.file_search_stores.documents.list(parent=store_name)

    deleted = 0
    for doc in docs:
        # Parse ISO timestamp
        created = datetime.fromisoformat(doc.create_time.replace('Z', '+00:00'))

        if created < cutoff:
            print(f'Deleting old document: {doc.display_name} (created {created.date()})')
            client.file_search_stores.documents.delete(name=doc.name)
            deleted += 1

    print(f'Deleted {deleted} documents older than {days_old} days')

delete_old_documents('fileSearchStores/abc123', days_old=90)
```

## Best Practices

### 1. Always Check State

```python
# Before querying
docs = client.file_search_stores.documents.list(parent=store.name)
active = [d for d in docs if d.state == 'STATE_ACTIVE']

if not active:
    raise Exception('No active documents in store')
```

### 2. Handle Failed Documents

```python
def check_failed_documents(store_name):
    """Alert on failed documents"""
    docs = client.file_search_stores.documents.list(parent=store_name)
    failed = [d for d in docs if d.state == 'STATE_FAILED']

    if failed:
        print(f'⚠️  {len(failed)} documents failed processing:')
        for doc in failed:
            print(f'  - {doc.display_name}')
        return False
    return True
```

### 3. Use Consistent Metadata

```python
METADATA_SCHEMA = {
    'department': ['Finance', 'Engineering', 'HR'],
    'year': ['2024', '2023'],
    'category': ['financial', 'technical', 'legal']
}

def validate_metadata(metadata):
    """Ensure metadata follows schema"""
    for item in metadata:
        key = item['key']
        value = item['string_value']

        if key in METADATA_SCHEMA:
            if value not in METADATA_SCHEMA[key]:
                raise ValueError(f'Invalid {key}: {value}')
```

### 4. Monitor Processing Time

```python
import time

start = time.time()
operation = client.file_search_stores.upload_to_file_search_store(...)

while not operation.done:
    operation = client.operations.get(name=operation.name)
    time.sleep(2)

duration = time.time() - start
print(f'Processing took {duration:.1f} seconds')

if duration > 300:  # 5 minutes
    print('⚠️  Unusually long processing time')
```

## Error Handling

### Common Errors

**Document Not Found:**
```python
try:
    doc = client.file_search_stores.documents.get(name='fileSearchStores/.../invalid')
except Exception as e:
    if 'not found' in str(e).lower():
        print('Document does not exist')
```

**Still Processing:**
```python
def ensure_document_ready(doc_name):
    doc = client.file_search_stores.documents.get(name=doc_name)

    if doc.state == 'STATE_PENDING':
        raise Exception('Document still processing, try again later')
    elif doc.state == 'STATE_FAILED':
        raise Exception('Document processing failed')

    return doc
```

## Limits

| Limit | Value |
|-------|-------|
| Max file size | 100 MB |
| Max documents per store | Unlimited (storage limited) |
| Max metadata pairs | 20 per document |
| Max display name length | 256 characters |
| Processing time (typical) | 30-60 seconds |
| Processing time (max) | 5-10 minutes for large files |

## Next Steps

- [Stores API →](./stores)
- [Query API →](./query)
- [Document Concepts →](../concepts/documents)
- [Upload Guide →](../guides/upload-documents)
