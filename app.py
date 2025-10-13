from flask import Flask, jsonify
from dotenv import load_dotenv
from db import db
import os

load_dotenv()

app = Flask(__name__) # App base
# CFGs
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL") # URL Database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Requerimento
# End CFGs
db.init_app(app)

# Blueprints

from routes.medios import bp_medios

app.register_blueprint(bp_medios, url_prefix="/api/medios")


if __name__ == '__main__':
    app.run(debug = True, port = 5001)