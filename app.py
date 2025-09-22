from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
from apis.users import users_bp
from apis.recipes import recipes_bp
from apis.comments import comments_bp
from apis.notifications import notifications_bp
from apis.images import images_bp
import os

load_dotenv()

app = Flask(__name__)


CORS(
    app,
    origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "Accept"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
)


@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Vary"] = "Origin"  # allow multiple origins dynamically
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    return response


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


app.register_blueprint(users_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(images_bp)


connect(
    db="recipehub",
    host="mongodb://localhost:27017/recipehub"
)


@app.route("/")
def home():
    return {"message": "Recipehub backend is running"}

if __name__ == "__main__":
    app.run(debug=True, port=5500)
