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
            'participants': [participant.to_json() for participant in self.participants],
            'created_at': self.created_at.timestamp(),
            'updated_at': self.updated_at.timestamp(),
        }


class MessageRecipients(db.EmbeddedDocument):
    recipient = db.ReferenceField(UserLoginInfo)
    room = db.ReferenceField(ChatRoom)
    is_received = db.ListField(db.ReferenceField(UserLoginInfo), default=list)
    is_read = db.ListField(db.ReferenceField(UserLoginInfo), default=list)

    def to_json(self):
        return {
            'is_received': self.is_received,
            'is_read': self.is_read,
            'room': self.room.to_json()
        }


class MessageMedia(db.EmbeddedDocument):
    link = db.URLField(required=False)
    caption = db.StringField(required=False)


class Message(AbstractBaseModel):
    sender = db.ReferenceField(UserLoginInfo)
    type = db.StringField(choices=MESSAGE_TYPES, default=DEFAULT_MESSAGE_TYPE, required=True)
    message_body = db.StringField(required=True)
    message_media = db.EmbeddedDocumentField(MessageMedia)
    is_sent = db.BooleanField(default=False)
    recipients = db.EmbeddedDocumentListField(MessageRecipients)

    def to_json(self, *args, **kwargs):
        return {
            'sender': self.sender.to_json(),
            'type': self.type,
            'message_body': self.message_body,
            'message_media': self.message_media,
            'is_sent': self.is_sent,
            'recipients': [recipient.to_json() for recipient in self.recipients],
            'created_at': self.created_at.timestamp(),
            'updated_at': self.updated_at.timestamp(),
        }
