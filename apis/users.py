from flask import Blueprint, request, jsonify, current_app
from models.user import User
from utils.jwt_utils import token_required
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


#__________
#Get a user by ID
#__________

@users_bp.route("/users/<user_id>", methods=["GET"])
@token_required
def get_user_by_id(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

#__________
#Get a recipes by user ID
#__________

@users_bp.route("/users/<user_id>/recipes")
def get_user_recipes(user_id):
    user = User.objects(id = user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    recipes = Recipe.objects(user_id=user.id)
    if not recipes:
        return jsonify({"message": "This user has no recipes yet"}), 200

    return jsonify([recipe.to_dict for recipe in recipes])
#___________
#Get all users (protected)
#___________

@users_bp.route("/users", methods=["GET"])
@token_required
def get_all_users():
    users = User.objects()
    return jsonify([user.to_dict() for user in users])
 