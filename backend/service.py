import base64
from cobs import cobs
from datetime import datetime
import math

def decode_base64(data: str) -> bytes:
    return base64.b64decode(data)

def decode_cobs(data: bytes) -> bytes:
    return cobs.decode(data)

def decode_command(data: bytes) -> dict:
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
