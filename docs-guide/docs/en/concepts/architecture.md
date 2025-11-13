# Architecture Overview

Understand how Gemini File Search works under the hood.

## System Architecture

```mermaid
graph TB
    A[Your Application] -->|API Calls| B[Gemini File Search API]
    B --> C[File Search Stores]
    C --> D[Documents]
    D --> E[Chunks]
    E --> F[Embeddings]
    F --> G[Vector Search]

    H[User Query] --> I[Query Processing]
    I --> G
    G --> J[Relevant Chunks]
    J --> K[LLM Context]
    K --> L[Generated Answer + Citations]

    style B fill:#4285f4,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#34a853,stroke:#333,stroke-width:2px,color:#fff
    style L fill:#fbbc04,stroke:#333,stroke-width:2px
```

## Key Components

### 1. File Search Stores

**Purpose**: Containers for your documents

- One store per project or use case
- Tracks document metrics (active, pending, failed counts)
- Supports up to 1TB storage (paid tiers)

```python
store = client.file_search_stores.create(
    config={'display_name': 'My Project Docs'}
)
```

### 2. Documents

**Purpose**: Individual files you upload

- Support 100+ formats (PDF, DOCX, code, spreadsheets, etc.)
- Max 100MB per file (free tier)
- Progress through states: `PENDING` → `ACTIVE` → ready to query

```mermaid
stateDiagram-v2
    [*] --> PENDING: Upload
    PENDING --> ACTIVE: Processing Complete
    PENDING --> FAILED: Error
    ACTIVE --> [*]: Ready for Queries
    FAILED --> [*]: Check Format

    note right of PENDING
      Chunking & Embedding
      30-60 seconds
    end note

    note right of ACTIVE
      Can be queried
    end note
```

### 3. Automatic Chunking

**What Gemini Does For You**:
- Intelligently splits documents into semantic chunks
- Preserves context across chunk boundaries
- Handles different file formats appropriately

**You don't need to**:
- Choose chunk size
- Handle overlap
- Split documents manually

### 4. Embeddings & Vector Search

**Behind the Scenes**:
1. Each chunk gets an embedding vector
2. Your query gets an embedding vector
3. Semantic similarity finds relevant chunks
4. Results ranked by relevance

**You interact with**: High-level API (no vector math required)

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Your App
    participant G as Gemini API
    participant VS as Vector Search
    participant LLM as Gemini LLM

    U->>A: "What was Q2 revenue?"
    A->>G: generate_content(query, store)
    G->>VS: Embed query & search
    VS-->>G: Top 10 relevant chunks
    G->>LLM: Query + chunks as context
    LLM-->>G: Answer + source references
    G-->>A: Response with citations
    A-->>U: Display answer & sources
```

## Upload Workflow

```mermaid
flowchart LR
    A[File Selected] --> B{Validate Format}
    B -->|Invalid| C[Error: Unsupported]
    B -->|Valid| D{Check Size}
    D -->|>100MB| E[Error: Too Large]
    D -->|OK| F[Upload to Gemini]
    F --> G[Create Operation]
    G --> H{Poll Status}
    H -->|Not Done| H
    H -->|Done| I[Document ACTIVE]
    I --> J[Ready to Query]

    style F fill:#4285f4,color:#fff
    style I fill:#34a853,color:#fff
    style J fill:#fbbc04
```

## Storage Tiers

| Tier | Storage | File Limit | Use Case |
|------|---------|------------|----------|
| Free | 1 GB | 100 MB | Personal, testing |
| Tier 1 | 10 GB | 100 MB | Small teams |
| Tier 2 | 100 GB | 100 MB | Medium projects |
| Tier 3 | 1 TB | 100 MB | Enterprise |

:::tip Performance
Keep stores <20GB for best latency. Create multiple stores for large datasets.
:::

## Integration Patterns

### Pattern 1: Single Store per User

```python
# User-specific document isolation
store = create_store(f'user-{user_id}-docs')
```

**Use case**: Personal document assistant, per-user knowledge base

### Pattern 2: Single Store per Project

```python
# Project-wide knowledge base
store = create_store(f'project-{project_id}-docs')
```

**Use case**: Team collaboration, shared documentation

### Pattern 3: Multiple Stores with Metadata

```python
# Separate by category, query across multiple
financial_store = create_store('financial-docs')
technical_store = create_store('technical-docs')

# Query both
response = query(
    'Find budget info',
    store_names=[financial_store.name, technical_store.name]
)
```

**Use case**: Large-scale document management, multi-category search

## Security & Access Control

**API Key Level**: All stores share same API key permissions

**Application Level**: Implement your own access control:

```python
# Example: User can only access their stores
def user_can_access_store(user_id: str, store_name: str) -> bool:
    # Check database for ownership
    return store_owner_id == user_id
```

## Performance Considerations

### Query Speed
- **First query**: ~2-3 seconds (cold start)
- **Subsequent queries**: ~500ms-1s
- **Store size impact**: <20GB optimal

### Upload Speed
- **Small files (<1MB)**: 5-10 seconds
- **Medium files (10MB)**: 30-60 seconds
- **Large files (50MB+)**: 2-5 minutes

### Optimization Tips
1. **Batch uploads** when possible
2. **Use metadata filters** to narrow search space
3. **Keep stores focused** (single topic/project)
4. **Monitor document states** before querying

## Next Steps

- [Understand Stores →](/en/concepts/stores)
- [Document Lifecycle →](/en/concepts/documents)
- [Semantic Search Deep Dive →](/en/concepts/semantic-search)
- [FastAPI Integration →](/en/guides/fastapi-integration)
