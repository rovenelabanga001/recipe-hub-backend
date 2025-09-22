from flask import Blueprint, jsonify, send_file
from mongoengine import get_db
from bson import ObjectId
from gridfs import GridFS
import io

images_bp = Blueprint("images", __name__)


@images_bp.route("/api/images/<image_id>")
def serve_image(image_id):
    try:
        db = get_db()
        fs = GridFS(db)
        
        file = fs.get(ObjectId(image_id))

        image_stream = io.BytesIO(file.read())

        return send_file(image_stream, mimetype=file.content_type, download_name=f"{image_id}.jpg")
    except Exception as e:
        print(f"[ERROR] Failed to fetch {image_id} : {e}")
        return jsonify({"error": "Image not found", "details": str(e)}), 404