import datetime

from mongoengine import Document, StringField, DateTimeField

class BlackList(Document):
    jti = StringField(required=True, unique=True, sparse = True)
    blacklisted_on = DateTimeField(default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "jti": self.jti,
            "blacklisted_on": self.blacklisted_on.isoformat()
        }