from flask import Blueprint, request, jsonify
from models.recipe import Recipe
from models.user import User
from models.comment import Comment
from models.notification import Notification
from utils.crud_factory import crud_factory
from utils.crud_utils import get_document_or_404, update_document_fields
from utils.jwt_utils import token_required
from werkzeug.utils import secure_filename
import random, json
from datetime import datetime, timedelta


_last_random_refresh = None
_last_random_recipes = []

recipes_bp = Blueprint("recipes", __name__)

@recipes_bp.before_request
@token_required
def require_token():
    # This ensures token_required runs before every request to this blueprint
    pass

crud_factory(
    recipes_bp, 
    Recipe, 
    "recipes", 
    [
        "name", 
        "title", 
        "image",
        "prepTime", 
        "cookTime", 
        "servings", 
        "ingredients", 
        "directions", 
        "tags", 
        "category"
    ], 
    user_owned=True,exclude_methods=["POST", "PATCH"]
)

#___________
#Get quick recipes
#___________
@recipes_bp.route("/recipes/quick-meals/<int:max_cook_time>", methods=["GET"])
def get_quick_recipes(max_cook_time):
    if max_cook_time <= 0:
        return jsonify({"error": "Max cook time must be greater than 0"}), 400

    try:
        recipes = Recipe.objects(cookTime__lte=max_cook_time).order_by('cookTime')

        if not recipes:
            return jsonify({
                "message": f"No recipes found with cook time less than {max_cook_time} minutes",
                "data": [],
                "max_cook_time":max_cook_time
            }), 200
    
        return jsonify({
            "message": f"Found {len(recipes)} recipes with cook time ≤ {max_cook_time} minutes",
            "data": [recipe.to_dict() for recipe in recipes],
            "max_cook_time": max_cook_time
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to query recipes",
            "details": str(e)
        }), 500

#___________
#Get recipe's comments
#___________
@recipes_bp.route("/recipes/<recipe_id>/comments", methods=["GET"])
def get_recipe_comments(recipe_id):
    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    comments = Comment.objects(recipe=recipe)
    return jsonify([{
        "id": str(comment.id),
        "body": comment.body,
        "username": comment.user.username if comment.user else None,
        "time": comment.time.isoformat()
    }for comment in comments]), 200


#___________
#Get popular recipes
#___________
@recipes_bp.route("/recipes/popular", methods = ["GET"])
def get_popular_recipes():
    global _last_random_refresh, _last_random_recipes

    all_recipes = list(Recipe.objects)
    sorted_recipes = sorted(all_recipes, key=lambda r: len(r.likedBy), reverse=True)

    # Pick top 4 with likes > 0
    top_recipes = [r for r in sorted_recipes if len(r.likedBy) > 0][:4]

    if top_recipes:
        return jsonify({
            "message": "Top 4 popular recipes",
            "data": [recipe.to_dict() for recipe in top_recipes]
        }), 200

    # Fallback: random recipes (refresh every 4 hours)
    now = datetime.utcnow()
    if not _last_random_recipes or not _last_random_refresh or (now - _last_random_refresh > timedelta(hours=4)):
        _last_random_recipes = random.sample(all_recipes, min(4, len(all_recipes)))
        _last_random_refresh = now

    return jsonify({
        "message": "Random 4 recipes (fallback)",
        "data": [r.to_dict() for r in _last_random_recipes]
    }), 200

#___________
#Get user for a specific recipe
#___________
@recipes_bp.route("/recipes/<recipe_id>/user", methods=["GET"])
def get_recipe_user(recipe_id):
    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    
    user = recipe.user
    if not user:
        return jsonify({"error": "User not found for this recipe"}), 404
    
    return jsonify({
        "id": str(user.id),
        "username": user.username,
    }), 200

#___________
#Add a recipe
#___________
@recipes_bp.route("/recipes", methods=["POST"])
def create_recipe():
    try:
        # Validate scalar fields
        required_fields = ["name", "title", "prepTime", "cookTime", "servings"]
        missing_fields = [f for f in required_fields if not request.form.get(f)]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        
        image = request.files.get("image")
        if not image:
            return jsonify({"error": "Image is required"}), 400

        
        try:
            ingredients = json.loads(request.form.get("ingredients", "[]"))
            directions = json.loads(request.form.get("directions", "[]"))
            tags = json.loads(request.form.get("tags", "[]"))
            category = json.loads(request.form.get("category", "[]"))
        except Exception:
            return jsonify({"error": "Invalid JSON format for arrays"}), 400

        
        if not ingredients or not directions or not category:
            return jsonify({"error": "Ingredients, directions and category are required"}), 400

        
        user = User.objects(id=request.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create recipe
        recipe = Recipe(
            name=request.form.get("name"),
            title=request.form.get("title"),
            prepTime=int(request.form.get("prepTime")),
            cookTime=int(request.form.get("cookTime")),
            servings=int(request.form.get("servings")),
            ingredients=ingredients,
            directions=directions,
            tags=tags,
            category=category,
            user=user
        )

        
        recipe.image.put(
            image,
            content_type=image.content_type,
            filename=image.filename
        )

        
        recipe.save()

        return jsonify({
            "message": "Recipe created successfully",
            "data": recipe.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

#___________
#Update a recipe
#___________
@recipes_bp.route("/recipes/<recipe_id>", methods=["PUT"])
def update_recipe(recipe_id):
    try:
        recipe = Recipe.objects(id=recipe_id).first()
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404

        
        if request.form.get("name"):
            recipe.name = request.form.get("name")
        if request.form.get("title"):
            recipe.title = request.form.get("title")
        if request.form.get("prepTime"):
            recipe.prepTime = int(request.form.get("prepTime"))
        if request.form.get("cookTime"):
            recipe.cookTime = int(request.form.get("cookTime"))
        if request.form.get("servings"):
            recipe.servings = int(request.form.get("servings"))

        
        try:
            if request.form.get("ingredients"):
                recipe.ingredients = json.loads(request.form.get("ingredients"))
            if request.form.get("directions"):
                recipe.directions = json.loads(request.form.get("directions"))
            if request.form.get("tags"):
                recipe.tags = json.loads(request.form.get("tags"))
            if request.form.get("category"):
                recipe.category = json.loads(request.form.get("category"))
        except Exception:
            return jsonify({"error": "Invalid JSON format for arrays"}), 400

        
        new_image = request.files.get("image")
        if new_image:
            recipe.image.replace(
                new_image,
                content_type=new_image.content_type,
                filename=new_image.filename
            )

        
        recipe.save()

        return jsonify({
            "message": "Recipe updated successfully",
            "data": recipe.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
#___________
#Toggle like
#___________
@recipes_bp.route("/recipes/<recipe_id>/like", methods=["POST"])
def toggle_like(recipe_id):
    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    
    user = User.objects(id=request.user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user in recipe.likedBy:
        recipe.likedBy.remove(user)
        recipe.save()

        Notification.objects(
            user = recipe.user,
            actor = user,
            recipe = recipe,
            type="favorite"
        ).delete()

        return jsonify({
            "message": f"You unliked recipe '{recipe.title}'",
            "likeCount":len(recipe.likedBy),
            "liked": False
        }), 200

    else:
        recipe.likedBy.append(user)
        recipe.save()


        if str(recipe.user.id) != str(user.id):
            Notification(
                user=recipe.user,
                actor = user,
                recipe=recipe,
                type="favorite",
                message=f"{user.username} liked your recipe '{recipe.title}'"
            ).save()

        return jsonify({
            "message": f"You liked recipe '{recipe.title}'",
            "likeCount": len(recipe.likedBy),
            "liked": True
        }), 200