# shell.py
from mongoengine import connect
connect(db="recipehub", host="mongodb://localhost:27017/recipehub")

from models.user import User
from models.recipe import Recipe
from models.comment import Comment
from models.notification import Notification

print("✅ Connected to MongoDB. Models imported.")
