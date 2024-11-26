import pytest
from api import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_process_valid_request(client):
    """Тест успешной обработки корректного запроса."""
    valid_data = {
        "externalId": "12345",
        "data": "AQECAgMEBQYHCAkKCw=="
    }
    response = client.post('/co-2', json=valid_data)
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert "measurements" in response.json

def test_process_invalid_json(client):
    """Тест обработки некорректного JSON."""
    response = client.post('/co-2', data="{invalid_json}", content_type="application/json")
    assert response.status_code == 400
    assert response.json["error"] == "Request body must be JSON"

def test_process_missing_fields(client):
    """Тест запроса с отсутствующими обязательными полями."""
    invalid_data = {"data": "AQECAgMEBQYHCAkKCw=="}
    response = client.post('co-2', json=invalid_data)
    assert response.status_code == 400
    assert response.json["error"] == "Missing required fields"

def test_process_invalid_base64(client):
    """Тест запроса с некорректной base64-строкой."""
    invalid_data = {
        "externalId": "12345",
        "data": "invalid_base64"
    }
    response = client.post('/co-2', json=invalid_data)
    assert response.status_code == 500
    assert "error" in response.json

def test_process_internal_error(client):
    """Тест обработки ошибок внутри сервиса."""
    invalid_data = {
        "externalId": "12345",
        "data": "AQ=="
    }
    response = client.post('/co-2', json=invalid_data)
    assert response.status_code == 500
    assert "error" in response.json
