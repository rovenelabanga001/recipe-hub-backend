from flask import Blueprint, jsonify, request
from models.recipe import Recipe
from models.user import User
from utils.jwt_utils import token_required
from utils.crud_utils import get_document_or_404, update_document_fields

recipes_bp = Blueprint("recipes", __name__)


#_______________
# Get all recipes
#_______________
@recipes_bp.route("/recipes", methods=["GET"])
@token_required

def get_all_recipes():
    recipes = Recipe.objects()
    return jsonify([recipe.to_dict() for recipe in recipes]), 200


#________________
# Get recipe by ID
#_________________

@recipes_bp.route("/recipes/<recipe_id>", methods=["GET"])
@token_required

def get_recipe_by_id(recipe_id):
    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify(recipe.to_dict()), 200


#________________
# Create a new recipe
#________________

@recipes_bp.route("/recipes", methods = ["POST"])
@token_required

def create_recipe():
    data = request.json

    required_fields = [
        "name", "title", "prepTime", "cookTime", "servings",
        "ingredients", "directions", "tags", "category"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing field {field}"}), 400


    user = User.objects(id = request.user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    recipe_data = {field: data[field] for field in required_fields}
    recipe_data["user"] = user

    recipe = Recipe(**recipe_data).save()

    return jsonify(recipe.to_dict()), 201


#_______________
#Update and Delete recipe
#_______________
@recipes_bp.route("/recipes/<recipe_id>", methods=["PATCH", "DELETE"])
@token_required

def update_recipe(recipe_id):
    user = User.objects(id=request.user_id).first()
    if not user:
        return jsonify({"error": "User not found!"}), 404

    recipe, err, code = get_document_or_404(Recipe, recipe_id, "Recipe Not Found")
    if not recipe:
        return jsonify(err), code

    if recipe.user.id != user.id:
        return jsonify({"error": "You do not have permission for this recipe"}), 403

    if request.method == "PATCH":
        updated_recipe = update_document_fields(recipe, request.get_json())
        return jsonify(updated_recipe.to_dict())

        
    elif request.method == "DELETE":
        recipe_name = recipe.name
        recipe.delete()

        return jsonify({"message": f"Recipe '{recipe_name}' deleted successfully"}), 200


    

