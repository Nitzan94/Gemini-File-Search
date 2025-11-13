---
layout: home

hero:
  name: Gemini File Search
  text: Build RAG Applications
  tagline: Interactive guide for Google's Gemini File Search API - Semantic search with citations, no manual chunking
  image:
    src: /logo.svg
    alt: Gemini File Search
  actions:
    - theme: brand
      text: Get Started
      link: /en/getting-started/setup
    - theme: alt
      text: Interactive Tutorial
      link: /en/tutorial/
    - theme: alt
      text: API Reference
      link: /en/api/stores

features:
  - icon: 🔍
    title: Semantic Search
    details: Natural language queries across your documents with AI-powered understanding
  - icon: 📚
    title: 100+ File Formats
    details: PDF, DOCX, code files, spreadsheets, and more - upload and search them all
  - icon: 🎯
    title: Source Citations
    details: Every answer includes citations showing exactly where information came from
  - icon: ⚡
    title: Managed Infrastructure
    details: No manual chunking or embeddings - Gemini handles everything automatically
  - icon: 🔐
    title: Metadata Filtering
    details: Filter searches by custom metadata (author, date, category, etc.)
  - icon: 🚀
    title: FastAPI Integration
    details: Production-ready patterns for building web applications

---

## Why Gemini File Search?

**Traditional RAG systems** require you to manually:
- Split documents into chunks
- Generate embeddings
- Manage vector databases
- Tune chunking strategies

**Gemini File Search** handles all of this automatically. Just upload files and start querying.

## Quick Example

```python
from google import genai

# Initialize
client = genai.Client(api_key='YOUR_KEY')

# Create store
store = client.file_search_stores.create(
    config={'display_name': 'My Documents'}
)

# Upload document
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name=store.name
)

# Query with citations
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What was the Q2 revenue?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)

print(response.text)  # AI answer with citations
```

## What You'll Learn

- **Getting Started**: Setup, API keys, first query (10 min)
- **Core Concepts**: Architecture, stores, documents, search (20 min)
- **Integration**: FastAPI patterns, production deployment (30 min)
- **Advanced**: Metadata filtering, troubleshooting, optimization (20 min)

## Ready to Start?

<div style="display: flex; gap: 1rem; margin-top: 2rem;">
  <a href="/en/getting-started/setup" style="padding: 0.75rem 1.5rem; background: #4285f4; color: white; border-radius: 8px; text-decoration: none; font-weight: 500;">
    📖 Read the Guide
  </a>
  <a href="/en/tutorial/" style="padding: 0.75rem 1.5rem; border: 2px solid #4285f4; color: #4285f4; border-radius: 8px; text-decoration: none; font-weight: 500;">
    🎓 Take the Tutorial
  </a>
</div>

## Resources

- [Official Gemini Docs](https://ai.google.dev/gemini-api/docs/file-search)
- [Get API Key](https://aistudio.google.com/apikey)
- [GitHub Repository](https://github.com/Nitzan94/Gemini-File-Search)
- [Python SDK](https://github.com/googleapis/python-genai)
