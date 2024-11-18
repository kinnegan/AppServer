import os
from flask import Flask, request, jsonify
from waitress import serve
from service import decode_command, process_measurements, decode_base64, decode_cobs
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": "Request body must be JSON"}), 400


@app.route('/process', methods=['POST'])
def handle_device_data():
    try:
        if not request.is_json:
            raise BadRequest()


        data = request.get_json()
        if "externalId" not in data or "data" not in data:
            return jsonify({"error": "Missing required fields"}), 400


        binary_data = decode_base64(data["data"])
        uncobs = decode_cobs(binary_data)
        command = decode_command(uncobs)
        measurements = process_measurements(command)
        return jsonify({"status": "success", "measurements": measurements}), 200
    except BadRequest as e:
        raise e
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    serve(app, host="0.0.0.0", port=port, threads=1)
