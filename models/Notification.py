from mongoengine import (
    Document, StringField, ReferenceField, DateTimeField, BooleanField
)

import datetime

class Notification(Document):
    user = ReferenceField("User", required = True, reverse_delete_rule = 2)

    actor = ReferenceField("User", required = True)

    recipe = ReferenceField("Recipe", required = True)

    comment = ReferenceField("Comment", required = True)

    type = StringField(required = True, choices = ["favorite", "comment"])
    message = StringField(required = True)

    createdAt= DateTimeField(required = True, default = datetime.datetime.utcnow)
    read= BooleanField(required = True, default = False) 

    def to_dict(self):
        return {
            "id" : self.id,
            "userId": str(self.user.id) if self.user else None,
            "type": self.type,
            "user": self.actor.username if self.actor else None,
            "message": self.message,
            "recipeId": str(self.recipe.id) if self.recipe else None,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "read": self.read,
            "commentId": str(self.comment.id) if self.comment else None
        }