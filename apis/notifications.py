from flask import Blueprint, jsonify, request
from models.notification import Notification
from models.user import User
from utils.jwt_utils import token_required
from utils.crud_factory import crud_factory
from utils.crud_utils import get_document_or_404, update_document_fields


notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.before_request
@token_required
def require_token():
    pass

crud_factory(notifications_bp, Notification, "notifications", ["user", "actor", "recipe", "type", "message"], user_owned = True, exclude_methods=["POST", "UPDATE", "DELETE"])