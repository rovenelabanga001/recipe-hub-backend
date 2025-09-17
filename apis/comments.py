from flask import Blueprint, jsonify, request
from models.comment import Comment
from models.user import User
from utils.jwt_utils import token_required
from utils.crud_factory import crud_factory
from utils.crud_utils import get_document_or_404, update_document_fields

comments_bp = Blueprint("comments", __name__)

@comments_bp.before_request
@token_required
def require_token():
    # This ensures token_required runs before every request to this blueprint
    pass

crud_factory(comments_bp, Comment, "comments",[ "body", "recipe"], user_owned = True )
