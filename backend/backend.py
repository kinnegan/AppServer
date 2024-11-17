import os
from flask import Flask, request, jsonify
from waitress import serve
from pymongo import MongoClient
from datetime import datetime, timezone
import base64
import struct
from cobs import cobs
import math

app = Flask(__name__)

def decode_base64(data):
    return base64.b64decode(data)

def decode_cobs(data):
    return cobs.decode(data)

def decode_command(data):
    if len(data) == 0:
        print("Нулевая длина команды")
        return None

    command = {
        'code': data[0],
        'len': data[1] + (data[2] << 8),
        'devType': data[3] + (data[4] << 8),
        'crc': data[5] + (data[6] << 8),
        'commandData': data[7:]
    }

    # Определение типа устройства
    dev_type_dict = {
        1: "Цельсиум",
        2: "Smart PadLock",
        3: "Цельсиум-2 (CO2)",
        4: "Цельсиум-2 (шум, свет)"
    }
    command['devType'] = dev_type_dict.get(command['devType'], "unknown")

    return command

def process_measurements(command):
    command_data = command['commandData']
    # Используем обычное деление, чтобы избежать округления в меньшую сторону
    mea_num = math.ceil((len(command_data) - 1) / 20)
    reason = command_data[0]

    measurements = []

    for i in range(mea_num):
        timestamp = (
                            command_data[1 + 16 * i] +
                            (command_data[2 + 16 * i] << 8) +
                            (command_data[3 + 16 * i] << 16) +
                            (command_data[4 + 16 * i] << 24)
                    ) * 1000
        date = datetime.fromtimestamp(timestamp / 1000.0)
        formatted_date = date.strftime('%d.%m.%Y')
        formatted_time = date.strftime('%H:%M:%S')

        measurement = {
            'reason': command_data[5 + 16 * i] + (command_data[6 + 16 * i] << 8),
            'date': formatted_date,
            'time': formatted_time,
            'timestamp': timestamp,
            'id': command['code'],  # Используется как externalId
            'temperature': command_data[5 + 16 * i] + (command_data[6 + 16 * i] << 8),
            'humidity': round(((command_data[7 + 16 * i] + (command_data[8 + 16 * i] << 8)) * 0.01), 1),
            'lux': command_data[9 + 16 * i] + (command_data[10 + 16 * i] << 8),
            'noise': command_data[11 + 16 * i] + (command_data[12 + 16 * i] << 8),
            'co2': command_data[13 + 16 * i] + (command_data[14 + 16 * i] << 8),
            'voltage': round(((command_data[15 + 16 * i] + (command_data[16 + 16 * i] << 8)) * 0.001), 2)
        }

        # Удаление значений, равных 65535
        if measurement['temperature'] == 65535:
            del measurement['temperature']
        if measurement['co2'] == 65535:
            del measurement['co2']

        # Коррекция температуры
        if command_data[6 + 16 * i] & 0x80:
            measurement['temperature'] = (measurement['temperature'] - 65536) * 0.01
        else:
            measurement['temperature'] *= 0.01
        measurement['temperature'] = round(measurement['temperature'], 1)

        measurements.append(measurement)

    return measurements

@app.route('/process', methods=['POST'])
def handle_device_data():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    else:
        try:
            data = request.get_json()
            external_id = data["externalId"]
            binary_data = decode_base64(data["data"])
            uncobs = decode_cobs(binary_data)
            command = decode_command(uncobs)
            measurements = process_measurements(command)
        except:  
            return jsonify({"message": "JSON received and parsed successfully", "data": data}), 200

#        return jsonify({
#            "status": "success",
#            "measurements": measurements
#        }), 200

if __name__ == '__main__':
    # Читаем порт из переменной окружения или используем 5000 по умолчанию
    port = int(os.getenv('PORT', 5000))
    serve(app, host="0.0.0.0", port=port, threads=1)