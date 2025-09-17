from flask import Blueprint, request, jsonify, current_app
from models.user import User
from models.blacklist import BlackList
from models.recipe import Recipe
from models.comment import Comment
from models.notification import Notification
from utils.jwt_utils import token_required
import bcrypt
import jwt
import datetime
import uuid

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

    recipes = Recipe.objects(user_id=user.id)
    if not recipes:
        return jsonify({"message": "This user has no recipes yet"}), 200

    return jsonify([recipe.to_dict for recipe in recipes])

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
                "message": f"User with username not found"
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
#__________
#Toggle Favorite Recipe
#__________

@users_bp.route("/users/favorites/<recipe_id>", methods=["POST"])
def toggle_favorite(recipe_id):
    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    user = User.objects(id=request.user_id).first()

    if recipe in user.favoriteRecipeIds:
        user.favoriteRecipeIds.remove(recipe)
        user.save()

        recipe.favoriteCount = max(0, recipe.favoriteCount - 1)
        recipe.save()

        Notification.objects(
        user=recipe.user,
        actor=user,
        recipe=recipe,
        type="favorite"
    ).delete()

        return jsonify({
            "message": f"Recipe '{recipe.title}' removed from favorites",
            "data": user.to_dict(),
            "favorited": False
        }), 200

    else:
        user.favoriteRecipeIds.append(recipe)
        user.save()

        recipe.favoriteCount += 1
        recipe.save()

        if str(recipe.user.id) != str(user.id):
            Notification(
                user = recipe.user,
                actor = user,
                recipe = recipe,
                type= "favorite",
                message=f"{user.username} liked your recipe '{recipe.title}'"
            ).save()

        return jsonify({
            "message":f"Recipe '{recipe.title}' added to favorites",
            "data": user.to_dict(),
            "favorited": True
  
        })
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
#Get all users (protected)
#___________

@users_bp.route("/users", methods=["GET"])
def get_all_users():
    users = User.objects()
    return jsonify([user.to_dict() for user in users])
 