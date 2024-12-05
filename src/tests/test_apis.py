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
#---
def test_print_routes():
    """Проверка вывода всех маршрутов."""
    with patch("builtins.print") as mock_print:
        from src.modules.apis import print_routes
        print_routes()
        mock_print.assert_any_call("/ - home")
        # Проверить, что каждый зарегистрированный маршрут был выведен.

def test_404(client):
    """Проверка обработки несуществующего маршрута."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

def test_invalid_api_post_missing_field(client):
    """Проверка POST-запроса на /api/test с отсутствующим обязательным полем."""
    payload = {
        "externalId": "test@123.iot.mts.ru",
        "niddConfiguration": "/3gpp-nidd/v1/test/configurations/123",
        "reliableDataService": False
        # Отсутствует обязательное поле "data"
    }
    response = client.post("/api/test", json=payload)
    
    # Проверяем, что ответ имеет статус 400
    assert response.status_code == 400

    # Проверяем, что ответ в формате JSON
    try:
        response_data = response.json()
    except ValueError:
        pytest.fail(f"Ответ не является валидным JSON: {response.data}")

    # Проверяем, что ответ содержит 'detail', где указано сообщение об ошибке
    assert "detail" in response_data, f"Ключ 'detail' отсутствует в ответе: {response_data}"
    
    # Проверяем, что в 'detail' содержится сообщение о недостающем поле
    assert "'data' is a required property" in response_data["detail"], f"Ожидаемое сообщение об ошибке не найдено: {response_data['detail']}"

def test_invalid_api_post_wrong_data_format(client):
    """Проверка POST-запроса на /api/test с некорректным форматом данных."""
    payload = {
        "externalId": "test@123.iot.mts.ru",
        "niddConfiguration": "/3gpp-nidd/v1/test/configurations/123",
        "reliableDataService": False,
        "data": "incorrect-data-format"  # Невалидные данные (проверить, если формат имеет значение)
    }
    response = client.post("/api/test", json=payload)
    
    # Проверяем, что ответ имеет статус 400
    assert response.status_code == 400

    # Вызываем response.json() для получения JSON данных
    response_data = response.json()
    
    # Проверяем, что ошибка связана с неправильным форматом
    assert "Ошибка декодирования base64" in response_data["error"] or "Ошибка обработки запроса" in response_data["error"]