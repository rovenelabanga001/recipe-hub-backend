from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

connect(
    db="recipehub",
    host="mongodb://localhost:27017/recipehub"
)

@app.route("/")
def home():
    return {"message": "Recipehub backend is running"}

if __name__ == "__main__":
    app.run(debug = True, port = 5500)