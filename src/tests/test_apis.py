import pytest
from modules.apis import app
from unittest.mock import patch

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_home(client):
    """Проверка главной страницы."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data

#def test_route(client):
#    response = client.post("/api/test", json={})
#    assert response.status_code != 404