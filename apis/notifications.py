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

crud_factory(notifications_bp, Notification, "notifications", ["user", "actor", "recipe", "type", "message"], user_owned = True, exclude_methods=["POST", "PATCH", "DELETE"])

@notifications_bp.route("/my-notifications/<notification_id>", methods=["PATCH"])
def update_notification(notification_id):
    
    data = request.json
    read = data.get("read")

    if read is not True:
        return jsonify({"error": "You can only mark notifications as read"}),400
    
    notification = Notification.objects(id=notification_id).first()
    if not notification:
        return jsonify({"error": "Notification not found"}), 200
    
    if notification.read:
        return jsonify({"message": "Notification already read"}), 200
    
    notification.read = True
    notification.save()

    return jsonify({
        "message":"Notification marked as read",
        "id": str(notification.id),
        "read": notification.read
    }), 200