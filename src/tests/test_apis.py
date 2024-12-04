import pytest,os,sys
print("PYTHONPATH:", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.modules.apis import app
from unittest.mock import patch


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    """Проверка главной страницы."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello, World!" in response.text

def test_route(client):
    response = client.post("/api/test", json={})
    assert response.status_code != 404
