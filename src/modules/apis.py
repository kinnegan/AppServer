import os
from flask import render_template
import connexion
from werkzeug.exceptions import BadRequest
import logging

logging.basicConfig(level=logging.DEBUG)
app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml", validate_responses=True)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host="0.0.0.0", port=port)
