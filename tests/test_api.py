# ABOUTME: Integration tests for Gemini File Search API
# ABOUTME: Tests store, document, and query operations

import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Load environment variables
load_dotenv()


@pytest.fixture
def client():
    """Create test client"""
    # Skip if no API key (don't fail in CI without key)
    if not os.getenv('GEMINI_API_KEY'):
        pytest.skip('GEMINI_API_KEY not set')

    from main import app
    return TestClient(app)


@pytest.fixture
def test_store(client):
    """Create test store and clean up after"""
    response = client.post('/api/stores', json={'display_name': 'Test Store'})
    assert response.status_code == 200
    store_data = response.json()
    store_id = store_data['name'].split('/')[1]

    yield store_id

    # Cleanup
    client.delete(f'/api/stores/{store_id}?force=true')


def test_create_store(client):
    """Test creating a store"""
    response = client.post('/api/stores', json={'display_name': 'My Test Store'})
    assert response.status_code == 200

    data = response.json()
    assert 'name' in data
    assert data['display_name'] == 'My Test Store'

    # Cleanup
    store_id = data['name'].split('/')[1]
    client.delete(f'/api/stores/{store_id}?force=true')


def test_list_stores(client):
    """Test listing stores"""
    # Create test store
    create_response = client.post('/api/stores', json={'display_name': 'List Test'})
    assert create_response.status_code == 200
    store_id = create_response.json()['name'].split('/')[1]

    # List stores
    response = client.get('/api/stores')
    assert response.status_code == 200

    data = response.json()
    assert 'stores' in data
    assert len(data['stores']) > 0

    # Cleanup
    client.delete(f'/api/stores/{store_id}?force=true')


def test_get_store(client, test_store):
    """Test getting single store with metrics"""
    response = client.get(f'/api/stores/{test_store}')
    assert response.status_code == 200

    data = response.json()
    assert 'name' in data
    assert 'display_name' in data
    assert 'active_documents_count' in data
    assert 'size_bytes' in data


def test_delete_store(client):
    """Test deleting store"""
    # Create store
    create_response = client.post('/api/stores', json={'display_name': 'Delete Me'})
    assert create_response.status_code == 200
    store_id = create_response.json()['name'].split('/')[1]

    # Delete store
    response = client.delete(f'/api/stores/{store_id}?force=true')
    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(f'/api/stores/{store_id}')
    assert get_response.status_code == 404


def test_upload_document(client, test_store, tmp_path):
    """Test uploading document"""
    # Create temp file
    test_file = tmp_path / 'test.txt'
    test_file.write_text('This is a test document for Gemini file search.')

    with open(test_file, 'rb') as f:
        response = client.post(
            f'/api/stores/{test_store}/upload',
            files={'file': ('test.txt', f, 'text/plain')},
            data={'display_name': 'Test Document'}
        )

    assert response.status_code == 200
    data = response.json()
    assert 'operation_name' in data
    assert data['message'] == 'Upload initiated'


def test_list_documents(client, test_store):
    """Test listing documents in store"""
    response = client.get(f'/api/stores/{test_store}/documents')
    assert response.status_code == 200

    data = response.json()
    assert 'documents' in data


def test_dashboard_page(client):
    """Test dashboard page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Gemini File Search' in response.content


def test_store_detail_page(client, test_store):
    """Test store detail page loads"""
    response = client.get(f'/stores/{test_store}')
    assert response.status_code == 200
    assert b'Upload Files' in response.content
