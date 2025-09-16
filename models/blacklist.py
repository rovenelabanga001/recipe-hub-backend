import datetime

from mongoengine import Document, StringField, DateTimeField

class BlackList(Document):
    token = StringField(required=True, unique=True)
    blacklisted_on = DateTimeField(default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "token": self.token,
            "blacklisted_on": self.blacklisted_on.isoformat()
        }