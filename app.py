from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
from apis.users import users_bp
from apis.recipes import recipes_bp
from apis.comments import comments_bp
from apis.notifications import notifications_bp
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.register_blueprint(users_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(notifications_bp)

connect(
    db="recipehub",
    host="mongodb://localhost:27017/recipehub"
)

@app.route("/")
def home():
    return {"message": "Recipehub backend is running"}

if __name__ == "__main__":
    app.run(debug = True, port = 5500)