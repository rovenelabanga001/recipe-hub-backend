from mongoengine import Document, StringField, ReferenceField, DateTimeField, CASCADE
import datetime

class Comment(Document):
    user = ReferenceField("User", required = True)
    recipe = ReferenceField("Recipe", required = True, reverse_delete_rule=CASCADE)
    body = StringField(required = True)
    time = DateTimeField(default=datetime.datetime.utcnow)

    def to_dict(self):
        return{
            "id": str(self.id),
            "username": self.user.username if self.user else None,
            "recipeId": str(self.recipe.id) if self.recipe else None,
            "body": self.body,
            "time": self.time.isoformat() if self.time else None,
        }