# ABOUTME: FastAPI routes for file search store operations
# ABOUTME: CRUD operations for stores with pagination

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .client import GeminiClient


router = APIRouter(prefix='/api/stores', tags=['stores'])


class CreateStoreRequest(BaseModel):
    display_name: Optional[str] = None


class DeleteStoreRequest(BaseModel):
    force: bool = False


@router.post('')
async def create_store(request: CreateStoreRequest):
    """Create new file search store"""
    try:
        client = GeminiClient()
        store = client.create_store(display_name=request.display_name)
        return {
            'name': store.name,
            'display_name': store.display_name,
            'create_time': store.create_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('')
async def list_stores(page_size: int = 10):
    """List all stores with pagination"""
    try:
        client = GeminiClient()
        stores = client.list_stores(page_size=page_size)
        return {
            'stores': [
                {
                    'name': s.name,
                    'display_name': s.display_name,
                    'create_time': s.create_time,
                    'update_time': s.update_time,
                    'active_documents_count': getattr(s, 'active_documents_count', 0),
                    'pending_documents_count': getattr(s, 'pending_documents_count', 0),
                    'failed_documents_count': getattr(s, 'failed_documents_count', 0),
                    'size_bytes': getattr(s, 'size_bytes', 0)
                }
                for s in stores
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{store_id}')
async def get_store(store_id: str):
    """Get single store with metrics"""
    try:
        client = GeminiClient()
        store = client.get_store(name=f'fileSearchStores/{store_id}')
        return {
            'name': store.name,
            'display_name': store.display_name,
            'create_time': store.create_time,
            'update_time': store.update_time,
            'active_documents_count': getattr(store, 'active_documents_count', 0),
            'pending_documents_count': getattr(store, 'pending_documents_count', 0),
            'failed_documents_count': getattr(store, 'failed_documents_count', 0),
            'size_bytes': getattr(store, 'size_bytes', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{store_id}')
async def delete_store(store_id: str, force: bool = False):
    """Delete store (force for cascade)"""
    try:
        client = GeminiClient()
        client.delete_store(name=f'fileSearchStores/{store_id}', force=force)
        return {'message': 'Store deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
