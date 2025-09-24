from flask import Blueprint, request, jsonify, current_app
from models.user import User
from models.blacklist import BlackList
from models.recipe import Recipe
from models.comment import Comment
from models.notification import Notification
from utils.jwt_utils import token_required
from mongoengine import get_db
from gridfs import GridFS
from bson import ObjectId
import bcrypt
import jwt
import datetime
import uuid
import os

DEFAULT_PROFILE_PICTURE_ID = os.getenv("DEFAULT_PROFILE_PIC_ID") 

users_bp = Blueprint("users", __name__)
@users_bp.before_request
def require_token():
    open_routes = {"/signup", "/signin"}
    if request.path in open_routes:
        return  

    return token_required(lambda: None)()

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
        missing_fields = []
        if not email:
            missing_fields.append("email")
        if not username:
            missing_fields.append("username")
        if not password:
            missing_fields.append("password")
    
        return jsonify({"error": f"Missing required field(s): {', '.join(missing_fields)}"}), 400


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

    jti = str(uuid.uuid4())  

    token = jwt.encode({
        "user_id": str(user.id),
        "email": user.email,     
        "username": user.username, 
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow(),
        "jti": jti
    }, current_app.config["SECRET_KEY"], algorithm="HS256")

    return  jsonify({"token": token, "user": user.to_dict()}), 200

#____________
#Signout
#____________
@users_bp.route("/signout", methods=["POST"])
def signout():
    jti = getattr(request, "jti", None)

    if not jti:
        return jsonify({"error": "Missing token identifier (jti)"}), 401

    # If not already blacklisted, save it
    if not BlackList.objects(jti=jti).first():
        BlackList(jti=jti).save()

    return jsonify({"message": "Successfully signed out"}), 200

#____________
#Get Current User
#____________
@users_bp.route("/users/me", methods=["GET"])
def get_current_user():
    user = User.objects(id=request.user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "favoriteRecipeIds": [str(rid.id) for rid in user.favoriteRecipeIds]  # ensure you map ReferenceField objects
    }), 200


    
#__________
#Get a user by ID
#__________

@users_bp.route("/users/id/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

#__________
#Get recipes by user ID
#__________

@users_bp.route("/users/<user_id>/recipes")
def get_user_recipes(user_id):
    user = User.objects(id = user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    recipes = Recipe.objects(user=user)
    if not recipes:
        return jsonify({"message": "This user has no recipes yet"}), 200

    return jsonify([recipe.to_dict() for recipe in recipes])

#___________
#Get top users
#___________
@users_bp.route("/top-users", methods=["GET"])
def get_top_users():
    try:
        # Aggregate recipes grouped by user_id
        pipeline = [
            {"$group": {"_id": "$user", "recipe_count": {"$sum": 1}}},
            {"$sort": {"recipe_count": -1}},
            {"$limit": 2}
        ]

        results = Recipe.objects.aggregate(*pipeline)

        top_users = []
        for result in results:
            user = User.objects(id=result["_id"]).first()
            if user:
                top_users.append({
                    "user": user.to_dict(),
                    "recipe_count": result["recipe_count"]
                })

        return jsonify({
            "message": "Top 2 users with the highest number of recipes",
            "data": top_users
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch top users",
            "details": str(e)
        }), 500

#___________
#Get user by username
#___________

@users_bp.route("/users/username/<string:username>", methods=["GET"])
def get_user_by_username(username):
    try:
        print("Looking for username:", username)

        user = User.objects(username=username).first()
        if not user:
            return jsonify({
                "message": f"User with username '{username}' not found"
            }), 404

        return jsonify({
            "message": f"User '{username}' found",
            "data": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch user",
            "details": str(e)
        }), 500


#___________
#Get users favorite recipes
#___________
@users_bp.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = User.objects(id=request.user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorites = [recipe.to_dict() for recipe in user.favoriteRecipeIds]

    return jsonify({
        "message": f"Found {len(favorites)} favorite recipes",
        "data": favorites
    }),200

#___________
#Get user's favorite recipe IDs
#___________

@users_bp.route("/users/me/favorites", methods=["GET"])
def get_my_favorites():
    user = User.objects(id=request.user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # favoriteRecipeIds is a list of Recipe references; return string ids
    fav_ids = [str(r.id) for r in (user.favoriteRecipeIds or [])]
    return jsonify({"favoriteRecipeIds": fav_ids}), 200

#___________
#Upload profile picture
#___________
@users_bp.route("/users/profile_picture", methods=["POST"])
def upload_profile_picture():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 2 * 1024 * 1024:
            return jsonify({"error": "File too large. Max size is 2MB"}), 400
        
        db = get_db()
        fs = GridFS(db)

        user = User.objects(id=request.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if user.profile_picture_id and user.profile_picture_id != DEFAULT_PROFILE_PICTURE_ID:
            try:
                fs.delete(ObjectId(user.profile_picture_id))
            except Exception as e:
                print(f"[WARN] failed to delete old profile picture: {e}")

        file_id = fs.put(file, filename=file.filename, content_type = file.content_type)

        user.profile_picture_id = str(file_id)
        user.save()

        return jsonify({
            "message": "Profile picture updated successfully",
            "data": user.to_dict()
        })
    
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return jsonify({"error": "Upload failed", "details": str(e)}), 500

#___________
#Reset profile picture
#___________

@users_bp.route("/users/profile_picture/reset", methods=["POST"])
def reset_profile_picture():
    try:
        db = get_db()
        fs = GridFS(db)

        user = User.objects(id=request.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if user.profile_picture_id and user.profile_picture_id != DEFAULT_PROFILE_PICTURE_ID:
            try:
                fs.delete(ObjectId(user.profile_picture_id))
            except Exception as e:
                print(f"[WARN] Failed to delete old profile picture: {e}")

        user.profile_picture_id = DEFAULT_PROFILE_PICTURE_ID
        user.save()

        return jsonify({
            "message": "Profile picture set to default",
            "data": user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": "Reset failed", "details": str(e)}), 500

#___________
#Get all users (protected)
#___________

# @users_bp.route("/users", methods=["GET"])
# def get_all_users():
#     users = User.objects()
#     return jsonify([user.to_dict() for user in users])
 