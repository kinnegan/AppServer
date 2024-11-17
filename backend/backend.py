import os
from flask import Flask, request, jsonify
from waitress import serve

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_json():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    return jsonify({"message": "JSON received and parsed successfully", "data": data}), 200

if __name__ == '__main__':
    # Читаем порт из переменной окружения или используем 5000 по умолчанию
#    port = int(os.getenv('PORT', 5000))
#    app.run(host='0.0.0.0', port=port)
 
    serve(app, host="0.0.0.0", port=5000, threads=1, debug=True)