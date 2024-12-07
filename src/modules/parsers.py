import base64
from cobs import cobs
from datetime import datetime, timezone
from pymongo import MongoClient
from flask import jsonify
import math
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Значение по умолчанию, если переменная не найдена
db_name = os.getenv("MONGO_DB", "co2")
# collection_name = os.getenv("MONGO_COLLECTION", "DeviceInfo")


client = MongoClient(mongo_uri)
db = client[db_name]
collection_device = db[os.getenv("MONGO_DEVICE_COLLECTION", "DeviceInfo")]
collection_data = db[os.getenv("MONGO_DATA_COLLECTION", "Measurements")]


def decode_base64(data: str) -> bytes:
    try:
        return base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Ошибка декодирования base64: {e}")


def decode_cobs(data: bytes) -> bytes:
    try:
        return cobs.decode(data)
    except Exception as e:
        raise ValueError(f"Ошибка COBS-декодирования: {e}")


def decode_command(data: bytes) -> dict:
    try:
        if len(data) == 0:
            raise ValueError("Нулевая длина команды")

        command = {
            'code': data[0],
            'len': data[1] + (data[2] << 8),
            'devType': data[3] + (data[4] << 8),
            # 'crc': data[3] + (data[4] << 8), # old version
            'crc': data[5] + (data[6] << 8),  # new version
            # 'commandData': data[5:] # old version
            'commandData': data[7:]  # new version
        }

        dev_type_dict = {
            1: "Цельсиум",
            2: "Smart PadLock",
            3: "Цельсиум-2 (CO2)",
            4: "Цельсиум-2 (шум, свет)"
        }
        command['devType'] = dev_type_dict.get(command['devType'], "unknown")
        return command
    except Exception as e:
        raise ValueError(f"Ошибка декодирования команды: {e}")


def process_measurements(command: dict, external_id: str, collection=None) -> list:
    if collection is None:
        collection = collection_data
  
    command_data = command['commandData']
    mea_num = math.ceil((len(command_data) - 1) / 20)
    measurements = []

    for i in range(mea_num):
        measurement = parse_measurement(command_data, i, command['code'], external_id)
        collection.insert_one(measurement)
        if measurement:
            measurements.append(measurement)

    return measurements


def parse_measurement(data: bytes, index: int, code: int, external_id: str) -> dict:
    start = 1 + 16 * index
    reason = (data[0])
    if len(data) < start + 16:
        raise ValueError(f": {len(data)},  {start + 16} ")

    timestamp = (data[1 + 16 * index] + (data[2 + 16 * index] << 8) + (data[3 + 16 * index] << 16) + (data[4 + 16 * index] << 24))
    date = datetime.fromtimestamp(timestamp, timezone.utc)
    temperature = (data[5 + 16 * index] + (data[6 + 16 * index] << 8)) * 0.01
    humidity = (data[7 + 16 * index] + (data[8 + 16 * index] << 8)) * 0.01
#    humidity = (data[7 + 20 * index] + (data[8 + 20 * index] + (data[9 + 20 * index] + (data[10 + 20 * index]<< 24)) * 0.01 #old version
#    pressure = (data[11 + 20 * index] + (data[12 + 20 * index] + (data[13 + 20 * index] + (data[14 + 20 * index]<< 24)) / 100 #old version
#    rawAir = (data[15 + 20 * index] + (data[16 + 20 * index] + (data[17 + 20 * index] + (data[18 + 20 * index]<< 24)) #old version
    lux = (data[9 + 16 * index] + (data[10 + 16 * index] << 8))
    noise = (data[11 + 16 * index] + (data[12 + 16 * index] << 8))
    co2 = (data[13 + 16 * index] + (data[14 + 16 * index] << 8))
    voltage = (data[15 + 16 * index] + (data[16 + 16 * index] << 8)) * 0.001
    measurement = {
        "id": code,
        "external_id": external_id,
        "reason": reason,
        "timestamp": timestamp,
        "datetime": date,
        "temperature": round(temperature, 2) if temperature != 65535 else None,
        "humidity": humidity if humidity != 65535 else None,
        "lux": lux if lux != 65535 else None,
        "noise": noise if noise != 65535 else None,
        "co2": co2 if co2 != 65535 else None,
        "voltage": round(voltage, 2),
        "date": date.strftime('%d-%m-%Y'),
        "time": date.strftime('%H:%M:%S')
    }

    return measurement


def parse_value(data: bytes, scale: float = 1.0) -> int:
    value = int.from_bytes(data, byteorder='big')
    return value * scale


def check_device(external_id: str, dev_type: str, app_id: str, config_id: str, collection=None):
    if collection is None:
        collection = collection_device

    try:
        check = collection.find_one({"external_id": external_id})
        if check is None:
            return add_device(external_id, dev_type, app_id, config_id, collection=collection)
        else:
            return update_device(external_id, collection=collection)
    except Exception as e:
        raise RuntimeError(f"Ошибка проверки устройства: {e}")


def add_device(external_id: str, dev_type: str, app_id: str, config_id: str, collection=None):
    if collection is None:
        collection = collection_device

    try:
        device = {
            "external_id": external_id,
            "dev_type": dev_type,
            "application_id": app_id,
            "config_id": config_id,
            "added": datetime.now(),
        }
        collection.insert_one(device)
        return "add"
    except Exception as e:
        raise RuntimeError(f"Ошибка добавления устройства: {e}")


def update_device(external_id: str, collection=None):
    if collection is None:
        collection = collection_device

    try:
        filter = {"external_id": external_id}
        last_head = {"$set": {"lastHeard": datetime.now()}}
        collection.update_one(filter, last_head)
        return "update"
    except Exception as e:
        raise RuntimeError(f"Ошибка обновления устройства: {e}")


def read(body):
    try:
        required_fields = ["externalId", "niddConfiguration", "data"]
        for field in required_fields:
            if field not in body:
                raise ValueError(f"Поле '{field}' отсутствует в запросе")
         
        external_id = body.get("externalId")
        nidd_config = body.get("niddConfiguration")
        reliable_service = body.get("reliableDataService")
        parse_nidd = nidd_config.split("/")
        app_id = parse_nidd[3]
        config_id = parse_nidd[5]
        payload_data = body.get("data")
        binary_data = decode_base64(payload_data)
        uncobs = decode_cobs(binary_data)
        command = decode_command(uncobs)
        measurements = process_measurements(command, external_id)
        x = check_device(external_id, command['devType'], app_id, config_id)
        return jsonify({"message": x})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Ошибка обработки запроса: {e}"}), 500
