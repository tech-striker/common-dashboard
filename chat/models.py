from app import db
from utils.constants import *
from utils.db.base_model import AbstractBaseModel
from authentication.models import UserLoginInfo


class ChatRoom(AbstractBaseModel):
    creator = db.ReferenceField(UserLoginInfo)
    is_group = db.BooleanField(default=True)
    admins = db.ListField(db.ReferenceField(UserLoginInfo), default=list)
    name = db.StringField(required=True)
    image = db.URLField(required=False)
    status = db.MultiLineStringField(required=False)
    participants = db.ListField(db.ReferenceField(UserLoginInfo), default=list)

    def to_json(self, *args, **kwargs):
        return {
            'id': str(self.pk),
            'creator_id': self.creator.to_json()['id'],
            'is_group': self.is_group,
            'admins': [admin.to_json() for admin in self.admins],
            'name': self.name,
            'image': self.image,
            'status': self.status,
            'participants': [participant.to_json() for participant in self.participants]
        }


class MessageRecipients(db.EmbeddedDocument):
    is_received = db.ListField(db.ReferenceField(UserLoginInfo), default=list)
    is_read = db.ListField(db.ReferenceField(UserLoginInfo), default=list)
    room = db.ReferenceField(ChatRoom)


class MessageMedia(db.EmbeddedDocument):
    link = db.URLField(required=False)
    caption = db.StringField(required=False)


class Message(AbstractBaseModel):
    sender = db.ReferenceField(UserLoginInfo)
    type = db.StringField(choices=MESSAGE_TYPES, default=DEFAULT_MESSAGE_TYPE, required=True)
    message_body = db.MultiLineStringField(required=True)
    message_media = db.EmbeddedDocumentField(MessageMedia)
    is_sent = db.BooleanField(default=False)
    recipients = db.EmbeddedDocumentListField(MessageRecipients)
