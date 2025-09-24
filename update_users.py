import os
from mongoengine import connect
from models.user import User

connect("recipehub", host="mongodb://localhost:27017/recipehub")

DEFAULT_PROFILE_PICTURE_ID = os.getenv("DEFAULT_PROFILE_PIC_ID")

for user in User.objects(profile_picture_id=None):
    user.profile_picture_id = DEFAULT_PROFILE_PICTURE_ID
    user.save()
    print(f"Updated user {user.username} with default profile pic")

