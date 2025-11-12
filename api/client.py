# ABOUTME: GenAI client wrapper for Gemini file search operations
# ABOUTME: Singleton pattern, provides stores, documents, query methods

import os
from typing import Optional
from google import genai
from google.genai import types


class GeminiClient:
    """Wrapper for Google GenAI client with file search capabilities"""

    _instance: Optional['GeminiClient'] = None
    _client: Optional[genai.Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError('GEMINI_API_KEY not found in environment')
            self._client = genai.Client(api_key=api_key)

    @property
    def client(self) -> genai.Client:
        """Get underlying GenAI client"""
        return self._client

    # Store operations
    def create_store(self, display_name: Optional[str] = None):
        """Create file search store"""
        config = {}
        if display_name:
            config['display_name'] = display_name
        return self._client.file_search_stores.create(config=config)

    def list_stores(self, page_size: int = 10):
        """List all file search stores"""
        return self._client.file_search_stores.list(config={'page_size': page_size})

    def get_store(self, name: str):
        """Get store by name with metrics"""
        return self._client.file_search_stores.get(name=name)

    def delete_store(self, name: str, force: bool = False):
        """Delete store (force=True for cascade delete)"""
        config = {'force': force} if force else {}
        return self._client.file_search_stores.delete(name=name, config=config)

    # Document operations
    def upload_document(
        self,
        file_path: str,
        store_name: str,
        display_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """Upload file to store"""
        config = {}
        if display_name:
            config['display_name'] = display_name
        if metadata:
            config['custom_metadata'] = [
                {'key': k, 'string_value': v}
                for k, v in metadata.items()
            ]

        return self._client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=store_name,
            config=config
        )

    def list_documents(self, store_name: str, page_size: int = 10):
        """List documents in store"""
        return self._client.file_search_stores.list_documents(
            file_search_store_name=store_name,
            config={'page_size': page_size}
        )

    def get_document(self, document_name: str):
        """Get document by name"""
        return self._client.file_search_stores.get_document(name=document_name)

    def delete_document(self, document_name: str, force: bool = True):
        """Delete document (force=True if has chunks)"""
        config = {'force': force} if force else {}
        return self._client.file_search_stores.delete_document(
            name=document_name,
            config=config
        )

    def query_document(
        self,
        document_name: str,
        query: str,
        results_count: int = 10,
        metadata_filters: Optional[list] = None
    ):
        """Query specific document"""
        config = {
            'query': query,
            'results_count': results_count
        }
        if metadata_filters:
            config['metadata_filters'] = metadata_filters

        return self._client.file_search_stores.query_document(
            name=document_name,
            config=config
        )

    # Query with generate_content
    def search(
        self,
        query: str,
        store_names: list[str],
        metadata_filter: Optional[str] = None,
        model: str = 'gemini-2.5-flash'
    ):
        """Semantic search across store(s) with citations"""
        tool_config = types.FileSearch(
            file_search_store_names=store_names
        )
        if metadata_filter:
            tool_config.metadata_filter = metadata_filter

        response = self._client.models.generate_content(
            model=model,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(file_search=tool_config)]
            )
        )
        return response

    # Operation polling
    def get_operation(self, operation_name: str):
        """Poll long-running operation status"""
        return self._client.file_search_stores.get_operation(name=operation_name)
