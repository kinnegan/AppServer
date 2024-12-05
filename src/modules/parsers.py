import base64
from cobs import cobs
from datetime import datetime
from pymongo import MongoClient
from flask import jsonify, request
import math

client = MongoClient("mongodb://192.168.1.5:27017/")
db = client["co2"]
collection = db["DeviceInfo"]

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
            'crc': data[5] + (data[6] << 8),
            'commandData': data[7:]
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

def process_measurements(command: dict) -> list:
    command_data = command['commandData']
    mea_num = math.ceil((len(command_data) - 1) / 20)
    measurements = []

    for i in range(mea_num):
        measurement = parse_measurement(command_data, i, command['code'])
        if measurement:
            measurements.append(measurement)

    return measurements

def parse_measurement(data: bytes, index: int, code: int) -> dict:
    start = 1 + 16 * index
    timestamp = int.from_bytes(data[start:start+4], byteorder='little') * 1000
    date = datetime.fromtimestamp(timestamp / 1000.0)
    measurement = {
        "id": code,
        "temperature": parse_value(data[start+5:start+7]),
        "humidity": round(parse_value(data[start+7:start+9]) * 0.01, 1),
        "lux": parse_value(data[start+9:start+11]),
        "noise": parse_value(data[start+11:start+13]),
        "co2": parse_value(data[start+13:start+15]),
        "voltage": round(parse_value(data[start+15:start+17]) * 0.001, 2),
        "date": date.strftime('%d.%m.%Y'),
        "time": date.strftime('%H:%M:%S')
    }

    return measurement if measurement["temperature"] != 65535 else None

def parse_value(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little')

def check_device(external_id: str, dev_type: str, app_id: str, config_id: str):
    try:
        check = collection.find_one({"external_id":external_id})
        if check is None: 
            return add_device(external_id, dev_type, app_id, config_id)
        else: 
            return update_device(external_id)
    except Exception as e:
        raise RuntimeError(f"Ошибка проверки устройства: {e}")

def add_device(external_id: str, dev_type: str, app_id: str, config_id: str):
    try:
        device = {
            "external_id": external_id,
            "dev_type": dev_type,
            "application_id": app_id,
            "config_id": config_id,
            "added": datetime.now(),
        }
        collection.insert_one(device)
        add = 'add'
        return add
    except Exception as e:
        raise RuntimeError(f"Ошибка добавления устройства: {e}")

def update_device(external_id: str):
    try:
        filter = {"external_id": external_id}
        last_head = { "$set": { 'lastHeard': datetime.now() } }
        collection.update_one(filter,last_head)
        upd = 'update'
        return upd
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
        measurements = process_measurements(command)
        x = check_device(external_id,command['devType'], app_id, config_id)
        return {"message": x}
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Ошибка обработки запроса: {e}"}), 500

