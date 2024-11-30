import pytest
from modules.apis import app

@pytest.fixture
def client():
    with app.app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_read_success(client, mocker):
    mocker.patch("modules.parsers.check_device", return_value="add")
    payload = {
        "externalId": "test@123.iot.mts.ru",
        "niddConfiguration": "/3gpp-nidd/v1/test/configurations/123",
        "reliableDataService": False,
        "data": "dGVzdA=="
    }
    response = client.post("/api/test", json=payload)
    assert response.status_code == 200
    assert response.json == {"message": "add"}
