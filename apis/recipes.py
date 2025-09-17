from flask import Blueprint, request, jsonify
from models.recipe import Recipe
from models.user import User
from models.comment import Comment
from utils.crud_factory import crud_factory
from utils.crud_utils import get_document_or_404, update_document_fields
from utils.jwt_utils import token_required

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
        "prepTime", 
        "cookTime", 
        "servings", 
        "ingredients", 
        "directions", 
        "tags", 
        "category"
    ], 
    user_owned=True
)

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


@recipes_bp.route("/recipes/<recipe_id>/comments", methods=["GET"])
@token_required
def get_recipe_comments(recipe_id):
    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    comments = Comment.objects(recipe=recipe)
    return jsonify([{
        "id": str(comment.id),
        "body": comment.body,
        "user": str(comment.user.id) if comment.user else None,
        "time": comment.time.isoformat()
    }for comment in comments]), 200
