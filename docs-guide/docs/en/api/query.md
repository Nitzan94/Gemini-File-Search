# Query API Reference

Complete reference for querying documents with Gemini File Search.

## Overview

Querying combines Gemini's language model with semantic search over your documents to provide natural language answers with citations.

## Basic Query

### Signature

```python
client.models.generate_content(
    model: str,
    contents: str | list,
    config: GenerateContentConfig
) -> GenerateContentResponse
```

### Parameters

- **model** (str, required): Model to use
  - `'gemini-2.5-flash'` - Fast, cost-effective (recommended)
  - `'gemini-2.0-pro'` - More capable for complex queries

- **contents** (str | list, required): Query text or conversation history
  - Simple: `'What was Q2 revenue?'`
  - Multi-turn: List of Content objects

- **config** (GenerateContentConfig, required): Configuration
  - `tools`: List of Tool objects (must include FileSearch)

### Returns

`GenerateContentResponse` object with:
- `text`: Answer string
- `candidates`: List of response candidates (usually 1)
  - `content`: Response content
  - `grounding_metadata`: Citations and sources
  - `finish_reason`: Why generation stopped
  - `safety_ratings`: Content safety scores

## Simple Query Example

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='your-api-key')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What was the Q2 revenue?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=['fileSearchStores/abc123']
            )
        )]
    )
)

print(response.text)
# "According to the Q2 Financial Report, revenue was $50 million..."
```

## Configuration Options

### FileSearch Tool

```python
types.Tool(
    file_search=types.FileSearch(
        file_search_store_names=['fileSearchStores/store-id', ...],
        metadata_filter='department=Finance AND year=2024'
    )
)
```

**Parameters:**
- `file_search_store_names` (list[str], required): Stores to search
  - Can specify multiple stores
  - Searches all stores simultaneously
  - Format: `['fileSearchStores/store-id']`

- `metadata_filter` (str, optional): AIP-160 filter expression
  - Narrows search to matching documents
  - Format: `'key=value AND other_key=value'`
  - Operators: `AND`, `OR`, `!=`, `()`

### Example with Metadata Filter

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What were the key achievements?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=['fileSearchStores/abc123'],
                metadata_filter='department=Finance AND year=2024 AND quarter=Q2'
            )
        )]
    )
)
```

### Example with Multiple Stores

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What are our security requirements?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[
                    'fileSearchStores/security-docs',
                    'fileSearchStores/compliance-docs',
                    'fileSearchStores/engineering-docs'
                ]
            )
        )]
    )
)
```

## Working with Responses

### Extract Answer Text

```python
response = client.models.generate_content(...)

# Get answer
answer = response.text
print(f'Answer: {answer}')
```

### Extract Citations

```python
response = client.models.generate_content(...)

print(f'Answer: {response.text}\n')
print('Citations:')

for candidate in response.candidates:
    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        for chunk in candidate.grounding_metadata.grounding_chunks:
            # Safe attribute access
            doc_name = 'Unknown'
            if hasattr(chunk, 'document_name'):
                doc_name = chunk.document_name.split('/')[-1]

            relevance = 0.0
            if hasattr(chunk, 'relevance_score'):
                relevance = chunk.relevance_score

            print(f'  - {doc_name} (relevance: {relevance:.2f})')
```

### Complete Response Structure

```python
response = client.models.generate_content(...)

# Basic answer
answer = response.text

# Model information
model_version = response.model_version

# Response candidates (usually 1)
for candidate in response.candidates:
    # The actual content
    content = candidate.content

    # Why generation stopped
    finish_reason = candidate.finish_reason
    # Values: 'STOP' (normal), 'MAX_TOKENS', 'SAFETY', etc.

    # Safety ratings
    for rating in candidate.safety_ratings:
        print(f'{rating.category}: {rating.probability}')

    # Citations (if available)
    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        for chunk in candidate.grounding_metadata.grounding_chunks:
            # Document name, relevance score, etc.
            pass
```

## Multi-Turn Conversations

### Basic Conversation

```python
from google.genai import types

# First query
response1 = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What was Q2 revenue?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)

print(f'Q: What was Q2 revenue?')
print(f'A: {response1.text}\n')

# Follow-up query with history
response2 = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        types.Content(role='user', parts=[types.Part(text='What was Q2 revenue?')]),
        types.Content(role='model', parts=[types.Part(text=response1.text)]),
        types.Content(role='user', parts=[types.Part(text='How does that compare to Q1?')])
    ],
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)

print(f'Q: How does that compare to Q1?')
print(f'A: {response2.text}')
```

### Conversation Manager

```python
class ConversationManager:
    def __init__(self, client, store_name):
        self.client = client
        self.store_name = store_name
        self.history = []

    def ask(self, question):
        """Ask a question with full conversation history"""
        # Add user question
        self.history.append(
            types.Content(role='user', parts=[types.Part(text=question)])
        )

        # Generate response
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=self.history,
            config=types.GenerateContentConfig(
                tools=[types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[self.store_name]
                    )
                )]
            )
        )

        # Add model response to history
        self.history.append(
            types.Content(role='model', parts=[types.Part(text=response.text)])
        )

        return response.text

    def reset(self):
        """Clear conversation history"""
        self.history = []

# Use it
conversation = ConversationManager(client, 'fileSearchStores/abc123')

print(conversation.ask('What was Q2 revenue?'))
# "$50 million"

print(conversation.ask('How does that compare to Q1?'))
# "Q2 revenue of $50M represents 25% growth from Q1's $40M"

print(conversation.ask('What drove the growth?'))
# "According to the report, growth was driven by..."

conversation.reset()  # Start fresh conversation
```

## Complete Examples

### Simple Q&A Function

```python
def ask_documents(question, store_id, metadata_filter=None):
    """Simple function to query documents"""
    store_name = f'fileSearchStores/{store_id}'

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name],
                    metadata_filter=metadata_filter
                )
            )]
        )
    )

    return response.text

# Use it
answer = ask_documents(
    question='What was Q2 revenue?',
    store_id='abc123',
    metadata_filter='department=Finance AND year=2024'
)
print(answer)
```

### Query with Full Response

```python
def query_with_citations(question, store_id):
    """Query and return answer with citations"""
    store_name = f'fileSearchStores/{store_id}'

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name]
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
                    'relevance': getattr(chunk, 'relevance_score', 0.0)
                })

    return {
        'answer': response.text,
        'citations': citations
    }

# Use it
result = query_with_citations(
    question='What was Q2 revenue?',
    store_id='abc123'
)

print(f"Answer: {result['answer']}\n")
print("Sources:")
for citation in result['citations']:
    print(f"  - {citation['document']} (relevance: {citation['relevance']:.2f})")
```

### Batch Queries

```python
def batch_query(questions, store_id):
    """Ask multiple questions"""
    store_name = f'fileSearchStores/{store_id}'
    results = []

    for question in questions:
        print(f'Asking: {question}')

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(
                tools=[types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )]
            )
        )

        results.append({
            'question': question,
            'answer': response.text
        })

    return results

# Use it
questions = [
    'What was Q2 revenue?',
    'How many employees joined?',
    'What are the key risks?'
]

results = batch_query(questions, 'abc123')

for result in results:
    print(f"\nQ: {result['question']}")
    print(f"A: {result['answer']}")
```

### Async Queries (FastAPI)

```python
import asyncio

async def async_query(question, store_id):
    """Async query for FastAPI endpoints"""
    loop = asyncio.get_event_loop()

    store_name = f'fileSearchStores/{store_id}'

    # Run blocking call in thread pool
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(
                tools=[types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )]
            )
        )
    )

    return response.text

# Use in FastAPI
@app.post('/query')
async def query_endpoint(question: str, store_id: str):
    answer = await async_query(question, store_id)
    return {'answer': answer}
```

## Error Handling

### Common Errors

**Store Not Found:**
```python
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='What was Q2 revenue?',
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=['fileSearchStores/invalid']
                )
            )]
        )
    )
except Exception as e:
    if 'not found' in str(e).lower():
        print('Store does not exist')
    else:
        raise
```

**No Active Documents:**
```python
# Validate before querying
store_name = 'fileSearchStores/abc123'
docs = list(client.file_search_stores.documents.list(parent=store_name))
active = [d for d in docs if d.state == 'STATE_ACTIVE']

if not active:
    raise Exception('Store has no active documents to query')

# Proceed with query
response = client.models.generate_content(...)
```

**Timeout:**
```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError('Query timeout')

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Use it
try:
    with timeout(30):
        response = client.models.generate_content(...)
        print(response.text)
except TimeoutError:
    print('Query took too long')
```

## Best Practices

### 1. Use Specific Questions

```python
# Vague - may use general knowledge
'Tell me about revenue'

# Specific - uses your documents
'According to the Q2 2024 financial report, what was total revenue?'
```

### 2. Filter for Performance

```python
# Slow - searches all documents
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=question,
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)

# Fast - searches only relevant documents
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=question,
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='department=Finance AND year=2024'
            )
        )]
    )
)
```

### 3. Handle Missing Citations

```python
response = client.models.generate_content(...)

# Safely check for citations
has_citations = False
for candidate in response.candidates:
    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        if candidate.grounding_metadata.grounding_chunks:
            has_citations = True
            break

if not has_citations:
    print('⚠️  Answer may use general knowledge, not your documents')
```

### 4. Cache Frequent Queries

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_query(question_hash, store_id):
    response = client.models.generate_content(...)
    return response.text

def ask(question, store_id):
    # Hash question for cache
    question_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
    return cached_query(question_hash, store_id)
```

## Model Comparison

| Feature | gemini-2.5-flash | gemini-2.0-pro |
|---------|------------------|----------------|
| Speed | Fast (~1-2s) | Slower (~3-5s) |
| Cost | Lower | Higher |
| Use case | Most queries | Complex analysis |
| Context window | Large | Large |

**Recommendation:** Use Flash for 95% of queries, Pro for complex analytical questions.

## Limits

| Limit | Value |
|-------|-------|
| Max query length | ~32,000 characters |
| Max response length | ~8,000 tokens |
| Max stores per query | Unlimited (practical: <10) |
| Query timeout | ~60 seconds |
| Typical latency | 2-3 seconds |

## Next Steps

- [Stores API →](./stores)
- [Documents API →](./documents)
- [Query Guide →](../guides/query)
- [Citations →](../concepts/citations)
