# ABOUTME: FastAPI routes for semantic search queries
# ABOUTME: Search across stores with metadata filtering and citations

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .client import GeminiClient


router = APIRouter(prefix='/api/query', tags=['query'])


class QueryRequest(BaseModel):
    query: str
    store_ids: list[str]
    metadata_filter: Optional[str] = None
    model: str = 'gemini-2.5-flash'


@router.post('')
async def search(request: QueryRequest):
    """Semantic search across store(s) with citations"""
    try:
        client = GeminiClient()

        # Build store names
        store_names = [f'fileSearchStores/{store_id}' for store_id in request.store_ids]

        # Perform search
        response = client.search(
            query=request.query,
            store_names=store_names,
            metadata_filter=request.metadata_filter,
            model=request.model
        )

        # Extract text - strip markdown formatting
        text = response.text if hasattr(response, 'text') else ''
        # Remove markdown: **bold**, *italic*, __bold__, _italic_
        import re
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **text**
        text = re.sub(r'__([^_]+)__', r'\1', text)      # __text__
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *text*
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _text_

        result = {
            'text': text,
            'citations': []
        }

        # Extract grounding metadata (citations)
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding = candidate.grounding_metadata
                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'retrieved_context'):
                            ctx = chunk.retrieved_context
                            citation = {
                                'title': getattr(ctx, 'title', ''),
                                'uri': getattr(ctx, 'uri', ''),
                            }
                            result['citations'].append(citation)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/document/{document_id}')
async def query_document(
    document_id: str,
    query: str,
    results_count: int = 10,
    metadata_filters: Optional[list] = None
):
    """Query specific document"""
    try:
        client = GeminiClient()
        response = client.query_document(
            document_name=document_id,
            query=query,
            results_count=results_count,
            metadata_filters=metadata_filters
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
