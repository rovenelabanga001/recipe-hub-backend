from mongoengine import (
    Document, StringField, IntField, ListField, ReferenceField, ImageField
)

class Recipe(Document):
    name = StringField(required = True)
    image = ImageField(size = (800, 600, True), thumbnail_size=(150, 150, True))
    title = StringField(required = True)
    prepTime = IntField(required = True)
    cookTime = IntField(required = True)
    servings = IntField(required = True)
    favoriteCount = IntField(default=0)

    ingredients = ListField(StringField(), required = True)
    directions = ListField(StringField(), required = True)
    tags = ListField(StringField(), required = True)
    category = ListField(StringField(), required = True)

    user = ReferenceField("User", required=True)

    def to_dict(self):
        return{
            "id": str(self.id),
            "name": self.name,
            "image": str(self.image.grid_id) if self.image else None,
            "title": self.title,
            "prepTime": self.prepTime,
            "cookTime": self.cookTime,
            "servings": self.servings,
            "ingredients": self.ingredients,
            "directions": self.directions,
            "tags": self.tags,
            "category": self.category,
            "userID": str(self.user.id) if self.user else None,
            "favoriteCount": self.favoriteCount
        }