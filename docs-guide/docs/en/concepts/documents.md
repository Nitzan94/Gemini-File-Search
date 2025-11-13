# Documents

Understanding document lifecycle, states, and formats.

## Document Lifecycle

<InteractiveDiagram
  :chart="`stateDiagram-v2
    [*] --> Upload: upload_to_file_search_store()
    Upload --> PENDING: Processing Started
    PENDING --> ACTIVE: Chunks + Embeddings Done
    PENDING --> FAILED: Error
    ACTIVE --> [*]: Ready to Query
    FAILED --> [*]: Check Error

    note right of PENDING
      30-60 seconds
      Chunking, embedding
    end note

    note right of ACTIVE
      Can be queried
    end note
`"
/>

## Document States

### STATE_PENDING
Document is being processed:
- Splitting into chunks
- Generating embeddings
- Building search index

**Duration:** 30-60 seconds (small files), 1-5 minutes (large files)

**Action:** Wait before querying

### STATE_ACTIVE
Document is ready:
- All chunks processed
- Embeddings generated
- Can be queried

**Action:** Query away!

### STATE_FAILED
Processing failed:
- Unsupported format
- Corrupted file
- Encoding issues

**Action:** Check format, re-upload

## Check Document State

```python
# List documents
docs = client.file_search_stores.documents.list(
    parent='fileSearchStores/store-id'
)

for doc in docs:
    print(f'{doc.display_name}: {doc.state}')

# Get specific document
doc = client.file_search_stores.documents.get(
    name='fileSearchStores/store-id/documents/doc-id'
)

if doc.state == 'STATE_ACTIVE':
    print('Ready to query!')
elif doc.state == 'STATE_PENDING':
    print('Still processing...')
elif doc.state == 'STATE_FAILED':
    print('Processing failed')
```

## Supported Formats

### Documents
- PDF (.pdf)
- Word (.docx, .doc)
- PowerPoint (.pptx, .ppt)
- Excel (.xlsx, .xls)
- Text (.txt)
- Markdown (.md)
- RTF (.rtf)
- ODT (.odt)

### Code
- Python (.py)
- JavaScript (.js, .ts)
- Java (.java)
- C/C++ (.c, .cpp, .h)
- Go (.go)
- Rust (.rs)
- Ruby (.rb)
- PHP (.php)

### Data
- CSV (.csv)
- TSV (.tsv)
- JSON (.json)
- YAML (.yaml, .yml)
- XML (.xml)

### Web
- HTML (.html)
- CSS (.css)
- SCSS (.scss)

### Archives
- ZIP (.zip) - auto-extracted

**Total:** 100+ formats supported

## File Size Limits

| Tier | Max File Size | Max Total Storage |
|------|--------------|-------------------|
| Free | 100 MB | 1 GB |
| Tier 1 | 100 MB | 10 GB |
| Tier 2 | 100 MB | 100 GB |
| Tier 3 | 100 MB | 1 TB |

:::warning
100MB per file limit applies to all tiers.
:::

## Document Properties

```python
doc = client.file_search_stores.documents.get(name='...')

doc.name                # Full resource name
doc.display_name        # Human-readable name
doc.state              # PENDING, ACTIVE, FAILED
doc.size_bytes         # File size
doc.mime_type          # 'application/pdf'
doc.create_time        # Upload timestamp
doc.update_time        # Last modified
doc.custom_metadata    # User metadata
```

## Custom Metadata

Add searchable metadata (max 20 key-value pairs):

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name=store_name,
    config={
        'display_name': 'Q4 Financial Report',
        'custom_metadata': [
            {'key': 'author', 'string_value': 'John Doe'},
            {'key': 'department', 'string_value': 'Finance'},
            {'key': 'year', 'string_value': '2024'},
            {'key': 'quarter', 'string_value': 'Q4'},
            {'key': 'category', 'string_value': 'financial'}
        ]
    }
)

# Query with metadata filter
# metadata_filter='department=Finance AND year=2024'
```

## Best Practices

1. **Wait for STATE_ACTIVE** before querying
2. **Use descriptive display names**
3. **Add relevant metadata** for filtering
4. **Check file size** before upload (<100MB)
5. **Verify format** is supported
6. **Use UTF-8 encoding** for text files
7. **Compress large files** when possible
8. **Monitor failed documents** and investigate

## Troubleshooting

### Documents stuck in PENDING

Wait longer - large files take time. Poll operation:

```python
while not operation.done:
    operation = client.operations.get(name=operation.name)
    time.sleep(2)
```

### Documents in FAILED state

Check:
1. File format supported?
2. File corrupted?
3. Correct encoding?
4. Under 100MB?

### Can't find document after upload

Wait for processing to complete - document won't appear until STATE_ACTIVE.

## Next Steps

- [Upload Documents Guide →](../guides/upload-documents)
- [Metadata Filtering →](../guides/metadata-filtering)
- [Semantic Search →](./semantic-search)
