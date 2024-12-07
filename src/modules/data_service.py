from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()


# Инициализация подключения к базе данных
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Значение по умолчанию, если переменная не найдена
db_name = os.getenv("MONGO_DB", "co2")

client = MongoClient(mongo_uri)
db = client[db_name]
collection_device = db[os.getenv("MONGO_DEVICE_COLLECTION", "DeviceInfo")]
collection_data = db[os.getenv("MONGO_DATA_COLLECTION", "Measurements")]

# Функция для получения списка устройств
def get_devices():
    collection = collection_device
    devices = collection.find({}, {"_id": 0, "external_id": 1, "dev_type": 1, "added": 1})
    return list(devices)

# Функция для получения агрегированных данных измерений
def get_measurements(device_id):
    collection = collection_data

    # Агрегация данных за последние 24 часа
    pipeline = [
        {
            "$match": { "external_id": device_id, "timestamp": { "$gte": datetime.today() - timedelta(days=1) } }
        },
        {
            "$group": {
                "_id": {
                    "year": { "$year": "$timestamp" },
                    "month": { "$month": "$timestamp" },
                    "day": { "$dayOfMonth": "$timestamp" },
                    "hour": { "$hour": "$timestamp" }
                },
                "avg_temperature": { "$avg": { "$toDouble": "$temperature" } },
                "avg_humidity": { "$avg": "$humidity" },
                "avg_co2": { "$avg": "$co2" }
            }
        },
        { "$sort": { "_id": 1 } }
    ]
    result = collection.aggregate(pipeline)
    return list(result)
