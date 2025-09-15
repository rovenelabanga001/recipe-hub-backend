from flask import Blueprint, jsonify, request
from models.comment import Comment,
from models.user import User,
from utils.jwt_utils import token_required

comments_bp = Blueprint("comments", __name__)

#_______________
# Get all comments
#_______________

@comments_bp.route