from mongoengine import Document, StringField, EmailField, ListField, ReferenceField
from flask_bcrypt import generate_password_hash, check_password_hash
from .recipe import Recipe  # import the Recipe model for reference


class User(Document):
    email = EmailField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)

    # Favorite recipes must be valid Recipe references
    favoriteRecipeIds = ListField(ReferenceField(Recipe))

    @classmethod
    def create(cls, email, username, password, favoriteRecipeIds=None):
        hashed_pw = generate_password_hash(password).decode("utf-8")
        return cls(
            email=email,
            username=username,
            password_hash=hashed_pw,
            favoriteRecipeIds=favoriteRecipeIds or []
        ).save()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "favoriteRecipeIds": [str(recipe.id) for recipe in self.favoriteRecipeIds]
        }
