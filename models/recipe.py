import datetime
from mongoengine import (
    Document, StringField, IntField, ListField, ReferenceField, FileField, DateTimeField
)

from flask import url_for

class Recipe(Document):
    name = StringField(required = True)
    image = FileField(required = True)
    title = StringField(required = True)
    prepTime = IntField(required = True)
    cookTime = IntField(required = True)
    servings = IntField(required = True)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)

    ingredients = ListField(StringField(), required = True)
    directions = ListField(StringField(), required = True)
    tags = ListField(StringField(), required = True)
    category = ListField(StringField(), required = True)

    user = ReferenceField("User", required=True)

    likedBy = ListField(ReferenceField("User"))

    def to_dict(self):
        image_url = None
        if self.image and self.image.grid_id:
            image_url = url_for("images.serve_image", image_id=str(self.image.grid_id), _external=True)


        return{
            "id": str(self.id),
            "name": self.name,
            "image": image_url,
            "title": self.title,
            "prepTime": self.prepTime,
            "cookTime": self.cookTime,
            "servings": self.servings,
            "ingredients": self.ingredients,
            "directions": self.directions,
            "tags": self.tags,
            "category": self.category,
            "userID": str(self.user.id) if self.user else None,
            "likesCount": len(self.likedBy),
            "createdAt":self.createdAt,
            "likedBy": [str(u.id) for u in self.likedBy] if self.likedBy else []
        }
    
