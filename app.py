from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
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



app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


app.register_blueprint(users_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(images_bp)


MONGODB_URI = os.getenv("MONGODB_URI")

# Connect MongoEngine
connect(host=MONGODB_URI)


@app.route("/")
def home():
    return {"message": "Recipehub backend is running"}

if __name__ == "__main__":
    app.run(debug=True, port=5500)
