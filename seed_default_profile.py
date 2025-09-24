from gridfs import GridFS
from bson import ObjectId
from mongoengine import connect, get_db

# Connect to Mongo
connect(
    db="recipehub",
    host="mongodb://localhost:27017/recipehub"
)

# Get database instance
db = get_db()
fs = GridFS(db)

# Upload default profile picture
with open("assets/images/default_profile.jpeg", "rb") as f:  # <-- fixed path
    file_id = fs.put(f, filename="default_profile.jpg", content_type="image/jpeg")

print("✅ Default profile picture uploaded with ID:", file_id)
