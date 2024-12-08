import os
from flask import render_template, request
from flask_cors import CORS
import connexion
import logging

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('swagger.yml', validate_responses=True)
CORS(app.app)


@app.app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.url}")
    if request.method == 'POST' and request.json:
        logger.info(f"Payload: {request.json}")


def print_routes():
    print("Registered API endpoints:")
    for rule in app.app.url_map.iter_rules():
        print(f"{rule} - {rule.endpoint}")


@app.route("/")
def home():
    print_routes()
    return render_template("home.html")


if __name__ == "__main__":
    port = int(os.getenv('SERVER_PORT', 8000))
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    app.run(host=port, port=port)
