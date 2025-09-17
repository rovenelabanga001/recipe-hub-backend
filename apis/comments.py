from flask import Blueprint, jsonify, request
from models.comment import Comment
from models.user import User
from models.notification import Notification
from models.recipe import Recipe
from utils.jwt_utils import token_required
from utils.crud_factory import crud_factory
from utils.crud_utils import get_document_or_404, update_document_fields

comments_bp = Blueprint("comments", __name__)

@comments_bp.before_request
@token_required
def require_token():
    # This ensures token_required runs before every request to this blueprint
    pass

crud_factory(comments_bp, Comment, "comments",[ "body", "recipe"], user_owned = True, exclude_methods=["POST"] )

@comments_bp.route("/comments", methods=["POST"])
@token_required
def create_comment():
    data = request.get_json() or {}

    recipe_id = data.get("recipe")
    body = data.get("body")

    if not recipe_id or not body:
        return jsonify({"error": "Missing recipe or body"}), 400

    recipe = Recipe.objects(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    user = User.objects(id=request.user_id).first()

    comment = Comment(user=user, recipe=recipe, body=body).save()

    if str(recipe.user.id) != str(user.id):
        Notification(
            user=recipe.user,
            actor=user,
            recipe=recipe,
            comment=comment,
            type="comment",
            message=f"{user.username} commented on your recipe '{recipe.title}'"
        ).save()

    return jsonify(comment.to_dict()), 201
