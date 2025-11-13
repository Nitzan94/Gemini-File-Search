# File Search Stores

Deep dive into stores - containers for your documents.

## What Are Stores?

Stores are containers that hold your documents. Think of them as:
- **Folders** for organizing documents
- **Databases** for semantic search
- **Namespaces** for access control

Each store:
- Has a unique name: `fileSearchStores/store-{id}`
- Contains multiple documents
- Tracks metrics (document counts, storage size)
- Can be queried independently or with other stores

## Store Properties

```python
store = client.file_search_stores.get(name='fileSearchStores/store-id')

# Properties
store.name                    # 'fileSearchStores/store-abc123'
store.display_name            # 'My Documents'
store.create_time             # '2024-11-13T10:30:00Z'
store.update_time             # '2024-11-13T12:00:00Z'
store.active_documents_count  # 10
store.pending_documents_count # 2
store.failed_documents_count  # 0
store.size_bytes             # 15728640 (15 MB)
```

## Store Limits

| Tier | Total Storage | Max File Size | Max Stores |
|------|--------------|---------------|------------|
| Free | 1 GB | 100 MB | Unlimited |
| Tier 1 | 10 GB | 100 MB | Unlimited |
| Tier 2 | 100 GB | 100 MB | Unlimited |
| Tier 3 | 1 TB | 100 MB | Unlimited |

:::tip Performance
Keep stores under 20 GB for optimal query latency.
:::

## Organization Patterns

### Pattern 1: One Store Per Project

```python
website_docs = client.file_search_stores.create(
    config={'display_name': 'Website Documentation'}
)
api_docs = client.file_search_stores.create(
    config={'display_name': 'API Reference'}
)
```

**Pros:** Clear separation, easy permissions
**Cons:** Can't query across projects easily

### Pattern 2: One Store with Metadata

```python
all_docs = client.file_search_stores.create(
    config={'display_name': 'All Company Docs'}
)

# Upload with category metadata
client.file_search_stores.upload_to_file_search_store(
    file='doc.pdf',
    file_search_store_name=all_docs.name,
    config={
        'custom_metadata': [
            {'key': 'category', 'string_value': 'website'},
            {'key': 'department', 'string_value': 'engineering'}
        ]
    }
)

# Query with filters
# metadata_filter='category=website'
```

**Pros:** Query across all documents, flexible filtering
**Cons:** All documents in one store

### Pattern 3: Per-User Stores

```python
def create_user_store(user_id):
    return client.file_search_stores.create(
        config={'display_name': f'User {user_id} Documents'}
    )
```

**Pros:** User isolation, privacy
**Cons:** More stores to manage

## Lifecycle Management

### Create

```python
store = client.file_search_stores.create(
    config={'display_name': 'Project Docs'}
)
```

### List

```python
stores = client.file_search_stores.list(config={'page_size': 20})
for store in stores:
    print(f'{store.display_name}: {store.active_documents_count} docs')
```

### Get Details

```python
store = client.file_search_stores.get(name='fileSearchStores/store-id')
print(f'Size: {store.size_bytes / 1024 / 1024:.2f} MB')
```

### Delete

```python
# Empty store
client.file_search_stores.delete(name='fileSearchStores/store-id')

# Store with documents (requires force)
client.file_search_stores.delete(
    name='fileSearchStores/store-id',
    config={'force': True}
)
```

## Best Practices

1. **Use descriptive names** - "Q4 Financial Reports 2024" not "Store 1"
2. **Keep stores focused** - One topic/project per store
3. **Monitor size** - Stay under 20GB for best performance
4. **Clean up old stores** - Delete unused stores regularly
5. **Document store purpose** - Track what each store contains

## Monitoring

```python
def check_store_health(store_name):
    store = client.file_search_stores.get(name=store_name)

    print(f'Store: {store.display_name}')
    print(f'Active: {store.active_documents_count}')
    print(f'Pending: {store.pending_documents_count}')
    print(f'Failed: {store.failed_documents_count}')
    print(f'Size: {store.size_bytes / 1024 / 1024:.2f} MB')

    if store.failed_documents_count > 0:
        print('⚠️  Some documents failed processing')

    if store.size_bytes > 20 * 1024 * 1024 * 1024:  # 20GB
        print('⚠️  Store size over 20GB - consider splitting')
```

## Next Steps

- [Understanding Documents →](./documents)
- [Upload Documents →](../guides/upload-documents)
- [Query Across Multiple Stores →](../api/query)
