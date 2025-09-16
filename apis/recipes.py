from flask import Blueprint, request, jsonify
from models.recipe import Recipe
from models.user import User
from utils.crud_factory import crud_factory
from utils.crud_utils import get_document_or_404, update_document_fields
from utils.jwt_utils import token_required

recipes_bp = Blueprint("recipes", __name__)

@recipes_bp.before_request
@token_required
def require_token():
    # This ensures token_required runs before every request to this blueprint
    pass

crud_factory(recipes_bp, Recipe, "recipes", ["name", "ingredients"], user_owned=True)