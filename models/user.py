from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, PULL
from flask_bcrypt import generate_password_hash, check_password_hash
from .recipe import Recipe  # import the Recipe model for reference
from flask import url_for
import os

DEFAULT_PROFILE_PICTURE_ID = os.getenv("DEFAULT_PROFILE_PIC_ID") 

class User(Document):
    email = EmailField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)

    profile_picture_id = StringField()

    # Favorite recipes must be valid Recipe references
    favoriteRecipeIds = ListField(ReferenceField(Recipe, reverse_delete_rule=PULL))

    @classmethod
    def create(cls, email, username, password, favoriteRecipeIds=None, profile_picture_id=None):
        hashed_pw = generate_password_hash(password).decode("utf-8")
        return cls(
            email=email,
            username=username,
            password_hash=hashed_pw,
            favoriteRecipeIds=favoriteRecipeIds or [],
            profile_picture_id=profile_picture_id or DEFAULT_PROFILE_PICTURE_ID
        ).save()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        # If the user has a non-default uploaded profile picture
        if self.profile_picture_id and str(self.profile_picture_id) != str(DEFAULT_PROFILE_PICTURE_ID):
            profile_pic_url = url_for("images.serve_image", image_id=self.profile_picture_id, _external=True)
        # Otherwise, fallback to default profile picture
        elif DEFAULT_PROFILE_PICTURE_ID:
            profile_pic_url = url_for("images.serve_image", image_id=DEFAULT_PROFILE_PICTURE_ID, _external=True)
        else:
            profile_pic_url = None  # optional fallback if no default is configured

        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "profile_pic": profile_pic_url,
        }


