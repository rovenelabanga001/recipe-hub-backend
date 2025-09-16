import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models.blacklist import BlackList

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Missing token!"}), 401

        # Check if token is blacklisted
        if BlackList.objects(token=token).first():
            return jsonify({"error": "Token has been blacklisted, please signin again"}), 401

        try:
            decoded = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            # ✅ Attach decoded user_id and token to request object
            request.user_id = decoded["user_id"]
            request.token = token

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(*args, **kwargs)
    return decorated
