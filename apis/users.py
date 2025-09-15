from flask import Blueprint, request, jsonify, current_app
from models.user import User
import bcrypt
import jwt
import datetime

users_bp = Blueprint("users", __name__)

#____________
#Signup
#____________
@users_bp.route("/signup", methods= ["POST"])
def signup():
    data = request.json
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.objects(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    if User.objects(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User.create(email=email, username=username, password=password )

    return jsonify(user.to_dict()), 201


#____________
#Signup
#____________
@users_bp.route("/signin", methods=["POST"])
def signin():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.objects(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode({
        "user_id": str(user.id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours = 2)
    },
    current_app.config["SECRET_KEY"],
    algorithm = "HS256"
    )

    return  jsonify({"token": token, "user": user.to_dict()}), 200


#___________
#Get all users (protected)
#___________

@users_bp.route("/users", methods=["GET"])
def get_users():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing token"}), 401

    try:
        decoded = jwt.decode(
            token.split("Bearer ")[-1],
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid Token"}), 401

    users = User.objects()
    return jsonify([u.to_dict() for u in users]), 200

    