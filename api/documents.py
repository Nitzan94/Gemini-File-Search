# ABOUTME: FastAPI routes for document operations in file search stores
# ABOUTME: Upload, list, get, delete documents with metadata support

import os
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from .client import GeminiClient


router = APIRouter(prefix='/stores', tags=['documents'])


@router.post('/{store_id}/upload')
async def upload_document(
    store_id: str,
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None)  # JSON string of key-value pairs
):
    """Upload file to store with optional metadata"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Parse metadata if provided
        metadata_dict = None
        if metadata:
            import json
            metadata_dict = json.loads(metadata)

        # Upload to Gemini
        client = GeminiClient()
        operation = client.upload_document(
            file_path=tmp_path,
            store_name=f'fileSearchStores/{store_id}',
            display_name=display_name or file.filename,
            metadata=metadata_dict
        )

        # Clean up temp file
        os.unlink(tmp_path)

        return {
            'operation_name': operation.name,
            'done': operation.done,
            'message': 'Upload initiated'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{store_id}/documents')
async def list_documents(store_id: str, page_size: int = 10):
    """List documents in store"""
    try:
        client = GeminiClient()
        documents = client.list_documents(
            store_name=f'fileSearchStores/{store_id}',
            page_size=page_size
        )
        return {
            'documents': [
                {
                    'name': d.name,
                    'display_name': d.display_name,
                    'create_time': d.create_time,
                    'update_time': d.update_time,
                    'state': d.state,
                    'size_bytes': d.size_bytes,
                    'mime_type': d.mime_type,
                    'custom_metadata': [
                        {'key': m.key, 'value': m.string_value}
                        for m in getattr(d, 'custom_metadata', [])
                    ]
                }
                for d in documents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/documents/{document_id}')
async def get_document(store_id: str, document_id: str):
    """Get single document"""
    try:
        client = GeminiClient()
        doc = client.get_document(
            document_name=f'fileSearchStores/{store_id}/documents/{document_id}'
        )
        return {
            'name': doc.name,
            'display_name': doc.display_name,
            'create_time': doc.create_time,
            'update_time': doc.update_time,
            'state': doc.state,
            'size_bytes': doc.size_bytes,
            'mime_type': doc.mime_type,
            'custom_metadata': [
                {'key': m.key, 'value': m.string_value}
                for m in getattr(doc, 'custom_metadata', [])
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{store_id}/documents/{document_id}')
async def delete_document(store_id: str, document_id: str):
    """Delete document (force=True for chunks)"""
    try:
        client = GeminiClient()
        client.delete_document(
            document_name=f'fileSearchStores/{store_id}/documents/{document_id}',
            force=True
        )
        return {'message': 'Document deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/operations/{operation_id}')
async def get_operation_status(operation_id: str):
    """Poll operation status"""
    try:
        client = GeminiClient()
        operation = client.get_operation(operation_name=operation_id)
        return {
            'name': operation.name,
            'done': operation.done,
            'metadata': getattr(operation, 'metadata', None)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
