import pytest
from datetime import datetime, timedelta
from mongomock import MongoClient as MockMongoClient
from src.modules.data_service import get_devices, get_measurements  # Замените `module` на имя вашего модуля

@pytest.fixture
def mock_collections():
    """
    Фикстура для создания фиктивной базы данных MongoDB
    и коллекций с тестовыми данными.
    """
    # Создаем клиент для имитации MongoDB
    client = MockMongoClient()
    db = client["test_db"]

    # Создаем коллекции
    devices_collection = db["DeviceInfo"]
    measurements_collection = db["Measurements"]

    # Наполняем коллекцию устройств данными
    devices_collection.insert_many([
        {"external_id": "device_1", "dev_type": "sensor", "added": datetime(2023, 1, 1)},
        {"external_id": "device_2", "dev_type": "sensor", "added": datetime(2023, 1, 2)},
    ])

    # Наполняем коллекцию измерений данными
    now = datetime.now()
    measurements_collection.insert_many([
        {"external_id": "device_1", "datetime": now - timedelta(hours=1), "temperature": 22.5, "humidity": 55, "co2": 400},
        {"external_id": "device_1", "datetime": now - timedelta(hours=2), "temperature": 21.0, "humidity": 60, "co2": 420},
        {"external_id": "device_2", "datetime": now - timedelta(hours=3), "temperature": 20.0, "humidity": 50, "co2": 390},
    ])

    return {
        "devices": devices_collection,
        "measurements": measurements_collection
    }


def test_get_devices(mock_collections):
    """
    Тест для функции get_devices.
    """
    devices = get_devices(collection=mock_collections["devices"])
    assert len(devices) == 2
    assert devices[0]["external_id"] == "device_1"
    assert devices[1]["external_id"] == "device_2"


def test_get_measurements(mock_collections):
    """
    Тест для функции get_measurements.
    """
    now = datetime.now()
    result = get_measurements("device_1", collection=mock_collections["measurements"])

    # Проверяем структуру результата
    assert "temperature" in result
    assert "humidity" in result
    assert "co2" in result

    # Проверяем данные
    assert len(result["temperature"]) == 2  # Данные за последние 24 часа
    assert result["temperature"][0]["avg_temperature"] == 21.0
    assert result["temperature"][1]["avg_temperature"] == 22.5

    # Проверяем timestamps
    assert result["temperature"][0]["timestamp"].endswith("Z")
    assert result["humidity"][0]["avg_humidity"] == 60
    assert result["co2"][0]["avg_co2"] == 420


def test_get_measurements_no_data(mock_collections):
    """
    Тест для функции get_measurements, если данных нет.
    """
    result = get_measurements("device_unknown", collection=mock_collections["measurements"])
    assert result == {"temperature": [], "humidity": [], "co2": []}
