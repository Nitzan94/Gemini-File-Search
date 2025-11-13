# Stores API Reference

Complete reference for working with file search stores.

## Store Resource

A store is a container that holds documents for semantic search.

### Store Properties

```python
store = client.file_search_stores.get(name='fileSearchStores/store-id')

# Properties
store.name                    # str: 'fileSearchStores/store-abc123'
store.display_name            # str: 'My Documents'
store.create_time             # str: '2024-11-13T10:30:00Z'
store.update_time             # str: '2024-11-13T12:00:00Z'
store.active_documents_count  # int: 10
store.pending_documents_count # int: 2
store.failed_documents_count  # int: 0
store.size_bytes             # int: 15728640 (15 MB)
```

## Methods

### create()

Create a new file search store.

**Signature:**
```python
client.file_search_stores.create(
    config: dict
) -> FileSearchStore
```

**Parameters:**
- `config` (dict, optional): Configuration options
  - `display_name` (str, optional): Human-readable name for the store

**Returns:**
- `FileSearchStore` object

**Example:**
```python
store = client.file_search_stores.create(
    config={'display_name': 'Product Documentation'}
)

print(f'Created: {store.name}')
print(f'Display name: {store.display_name}')
```

**Example without display name:**
```python
store = client.file_search_stores.create()
# Auto-generated name like 'Store abc123'
```

---

### list()

List all file search stores.

**Signature:**
```python
client.file_search_stores.list(
    config: dict = None
) -> Iterator[FileSearchStore]
```

**Parameters:**
- `config` (dict, optional): Configuration options
  - `page_size` (int, optional): Number of stores per page (default: 10, max: 100)

**Returns:**
- Iterator of `FileSearchStore` objects

**Example:**
```python
# List all stores
stores = client.file_search_stores.list(config={'page_size': 20})

for store in stores:
    print(f'{store.display_name}:')
    print(f'  Documents: {store.active_documents_count}')
    print(f'  Size: {store.size_bytes / 1024 / 1024:.2f} MB')
```

**Example with pagination:**
```python
# Get first page
stores = list(client.file_search_stores.list(config={'page_size': 10}))

# Iterate through all (pagination handled automatically)
for store in client.file_search_stores.list():
    process_store(store)
```

---

### get()

Get a specific store by name.

**Signature:**
```python
client.file_search_stores.get(
    name: str
) -> FileSearchStore
```

**Parameters:**
- `name` (str, required): Full store resource name (`fileSearchStores/store-id`)

**Returns:**
- `FileSearchStore` object

**Raises:**
- `NotFoundError`: Store does not exist

**Example:**
```python
store = client.file_search_stores.get(
    name='fileSearchStores/abc123'
)

print(f'Name: {store.display_name}')
print(f'Documents: {store.active_documents_count}')
print(f'Created: {store.create_time}')
```

**Error handling:**
```python
try:
    store = client.file_search_stores.get(name='fileSearchStores/nonexistent')
except Exception as e:
    print(f'Store not found: {e}')
```

---

### delete()

Delete a file search store.

**Signature:**
```python
client.file_search_stores.delete(
    name: str,
    config: dict = None
) -> None
```

**Parameters:**
- `name` (str, required): Full store resource name
- `config` (dict, optional): Configuration options
  - `force` (bool, optional): Delete even if store contains documents (default: False)

**Returns:**
- None

**Raises:**
- `FailedPreconditionError`: Store not empty and `force=False`
- `NotFoundError`: Store does not exist

**Example - empty store:**
```python
# Delete empty store
client.file_search_stores.delete(
    name='fileSearchStores/abc123'
)
```

**Example - store with documents:**
```python
# Must use force=True
client.file_search_stores.delete(
    name='fileSearchStores/abc123',
    config={'force': True}
)
```

**Safe deletion:**
```python
def safe_delete_store(store_name):
    """Delete store with confirmation"""
    store = client.file_search_stores.get(name=store_name)

    if store.active_documents_count > 0:
        print(f'Warning: Store has {store.active_documents_count} documents')
        confirm = input('Delete anyway? (yes/no): ')
        if confirm.lower() != 'yes':
            print('Deletion cancelled')
            return

    client.file_search_stores.delete(
        name=store_name,
        config={'force': True}
    )
    print('Store deleted')
```

---

### upload_to_file_search_store()

Upload a document to a store.

**Signature:**
```python
client.file_search_stores.upload_to_file_search_store(
    file: str | Path,
    file_search_store_name: str,
    config: dict = None
) -> Operation
```

**Parameters:**
- `file` (str | Path, required): Path to file to upload
- `file_search_store_name` (str, required): Full store resource name
- `config` (dict, optional): Configuration options
  - `display_name` (str, optional): Human-readable document name
  - `custom_metadata` (list[dict], optional): Metadata key-value pairs (max 20)
    - Each dict: `{'key': str, 'string_value': str}`

**Returns:**
- `Operation` object (long-running operation)

**Raises:**
- `InvalidArgumentError`: Invalid file format or too large
- `NotFoundError`: Store does not exist

**Basic example:**
```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name='fileSearchStores/abc123'
)

# Wait for completion
import time
while not operation.done:
    operation = client.operations.get(name=operation.name)
    time.sleep(2)

print('Upload complete!')
```

**With display name:**
```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='Q2_2024_Report_Final_v3.pdf',
    file_search_store_name=store.name,
    config={
        'display_name': 'Q2 2024 Financial Report'
    }
)
```

**With metadata:**
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
            {'key': 'category', 'string_value': 'financial'},
            {'key': 'status', 'string_value': 'final'}
        ]
    }
)
```

**Accessing uploaded document:**
```python
# Wait for completion
while not operation.done:
    operation = client.operations.get(name=operation.name)
    time.sleep(2)

# Get document from operation response
doc = operation.response.document
print(f'Document name: {doc.name}')
print(f'State: {doc.state}')
```

## Complete Examples

### Create and Populate Store

```python
import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv
import time

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Create store
store = client.file_search_stores.create(
    config={'display_name': 'Company Documentation'}
)
print(f'Created store: {store.name}')

# Upload multiple files
files = Path('docs').glob('*.pdf')

for filepath in files:
    print(f'Uploading {filepath.name}...')

    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(filepath),
        file_search_store_name=store.name,
        config={'display_name': filepath.stem}  # Filename without extension
    )

    # Wait for processing
    while not operation.done:
        operation = client.operations.get(name=operation.name)
        time.sleep(2)

    print(f'  ✓ {filepath.name} uploaded')

# Verify
store = client.file_search_stores.get(name=store.name)
print(f'\nTotal documents: {store.active_documents_count}')
```

### Monitor Store Usage

```python
def monitor_stores():
    """Display usage statistics for all stores"""
    stores = client.file_search_stores.list()

    print(f'{"Store":<30} {"Docs":<10} {"Size (MB)":<12} {"Status"}')
    print('-' * 70)

    total_size = 0
    for store in stores:
        size_mb = store.size_bytes / (1024 * 1024)
        total_size += size_mb

        status = '✓'
        if store.pending_documents_count > 0:
            status = f'⏳ {store.pending_documents_count} pending'
        elif store.failed_documents_count > 0:
            status = f'✗ {store.failed_documents_count} failed'

        print(f'{store.display_name:<30} {store.active_documents_count:<10} {size_mb:<12.2f} {status}')

    print('-' * 70)
    print(f'Total storage: {total_size:.2f} MB / 1024 MB (free tier)')
    print(f'Usage: {(total_size / 1024) * 100:.1f}%')

    if total_size > 900:
        print('⚠️  Warning: Approaching storage limit')

monitor_stores()
```

### Bulk Delete Old Stores

```python
from datetime import datetime, timedelta

def delete_old_stores(days_old=90):
    """Delete stores older than specified days"""
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    stores = client.file_search_stores.list()

    deleted = 0
    for store in stores:
        # Parse ISO timestamp
        created = datetime.fromisoformat(store.create_time.replace('Z', '+00:00'))

        if created < cutoff:
            print(f'Deleting old store: {store.display_name} (created {created.date()})')
            client.file_search_stores.delete(
                name=store.name,
                config={'force': True}
            )
            deleted += 1

    print(f'Deleted {deleted} stores older than {days_old} days')

delete_old_stores(days_old=90)
```

## Best Practices

### 1. Use Descriptive Names

```python
# Bad
store = client.file_search_stores.create()  # Auto-generated name

# Good
store = client.file_search_stores.create(
    config={'display_name': 'Q2 2024 Financial Documents'}
)
```

### 2. Check Before Deleting

```python
def safe_delete(store_name):
    store = client.file_search_stores.get(name=store_name)

    if store.active_documents_count > 0:
        print(f'Store has {store.active_documents_count} documents')
        return False

    client.file_search_stores.delete(name=store_name)
    return True
```

### 3. Monitor Storage

```python
def check_storage_limit():
    stores = client.file_search_stores.list()
    total_gb = sum(s.size_bytes for s in stores) / (1024**3)

    if total_gb > 0.9:  # 90% of 1GB
        raise Exception(f'Storage limit reached: {total_gb:.2f}GB / 1GB')
```

### 4. Handle Errors Gracefully

```python
try:
    store = client.file_search_stores.create(
        config={'display_name': 'My Store'}
    )
except Exception as e:
    print(f'Failed to create store: {e}')
    # Handle error appropriately
```

## Error Handling

### Common Errors

**Store Not Found:**
```python
try:
    store = client.file_search_stores.get(name='fileSearchStores/invalid')
except Exception as e:
    if 'not found' in str(e).lower():
        print('Store does not exist')
    else:
        raise
```

**Storage Limit Exceeded:**
```python
try:
    operation = client.file_search_stores.upload_to_file_search_store(...)
except Exception as e:
    if 'storage limit' in str(e).lower():
        print('Storage quota exceeded')
        # Clean up old stores or upgrade tier
    else:
        raise
```

**Store Not Empty:**
```python
try:
    client.file_search_stores.delete(name=store.name)
except Exception as e:
    if 'not empty' in str(e).lower():
        print('Store has documents, use force=True')
        client.file_search_stores.delete(name=store.name, config={'force': True})
    else:
        raise
```

## Limits

| Limit | Value |
|-------|-------|
| Max stores | Unlimited |
| Max store size (free tier) | 1 GB total across all stores |
| Max file size | 100 MB |
| Max display name length | 256 characters |
| Max metadata pairs per document | 20 |

## Next Steps

- [Documents API →](./documents)
- [Query API →](./query)
- [Upload Documents Guide →](../guides/upload-documents)
- [Store Concepts →](../concepts/stores)
