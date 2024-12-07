from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Инициализация подключения к базе данных
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
db_name = os.getenv("MONGO_DB", "co2")

client = MongoClient(mongo_uri)
db = client[db_name]
collection_device = db[os.getenv("MONGO_DEVICE_COLLECTION", "DeviceInfo")]
collection_data = db[os.getenv("MONGO_DATA_COLLECTION", "Measurements")]


# Функция для получения списка устройств
def get_devices(collection=None):
    if collection is None:
        collection = collection_device
    devices = collection.find({}, {"_id": 0, "external_id": 1, "dev_type": 1, "added": 1})
    return list(devices)


# Функция для получения агрегированных данных измерений
def get_measurements(device_id, collection=None):
    if collection is None:
        collection = collection_data

    # Получаем текущую дату и время в UTC
    now = datetime.now()
    day_ago = now - timedelta(days=1)

    # Агрегация данных за последние 24 часа
    pipeline = [
        {
            "$match": {
                "external_id": device_id,
                "datetime": {"$gte": day_ago}  # Сравниваем с UTC-объектом
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$datetime"},
                    "month": {"$month": "$datetime"},
                    "day": {"$dayOfMonth": "$datetime"},
                    "hour": {"$hour": "$datetime"}
                },
                "avg_temperature": {"$avg": "$temperature"},
                "avg_humidity": {"$avg": "$humidity"},
                "avg_co2": {"$avg": "$co2"}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    # Выполняем агрегацию
    result = list(collection.aggregate(pipeline))

    # Формируем данные в соответствии со спецификацией
    temperature_data = []
    humidity_data = []
    co2_data = []

    for item in result:
        # Формируем timestamp
        timestamp = datetime(
            year=item["_id"]["year"],
            month=item["_id"]["month"],
            day=item["_id"]["day"],
            hour=item["_id"]["hour"]
        ).isoformat() + "Z"  # Преобразуем в ISO 8601

        # Добавляем данные в соответствующие массивы
        temperature_data.append({
            "timestamp": timestamp,
            "avg_temperature": item.get("avg_temperature")
        })
        humidity_data.append({
            "timestamp": timestamp,
            "avg_humidity": item.get("avg_humidity")
        })
        co2_data.append({
            "timestamp": timestamp,
            "avg_co2": item.get("avg_co2")
        })

    # Возвращаем данные в формате, который соответствует спецификации
    return {
        "temperature": temperature_data,
        "humidity": humidity_data,
        "co2": co2_data
    }
