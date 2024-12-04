import os
from flask import render_template
import connexion
import logging

#logging.basicConfig(level=logging.DEBUG)
app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('swagger.yml', validate_responses=True)

def print_routes():
    print("Registered API endpoints:")
    for rule in app.app.url_map.iter_rules():
        print(f"{rule} - {rule.endpoint}")

@app.route("/")
def home():
    print_routes()
    return render_template("home.html")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host="0.0.0.0", port=port)
