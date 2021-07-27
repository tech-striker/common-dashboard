from mongoengine import *
from utils.constants import *
from utils.db.base_model import AbstractBaseModel
from authentication.models import UserLoginInfo


class ChatRoom(AbstractBaseModel):
    creator = ReferenceField(UserLoginInfo)
    is_group = BooleanField(default=True)
    admins = ListField(ReferenceField(UserLoginInfo), default=list)
    name = StringField(required=True)
    image = URLField(required=False)
    status = MultiLineStringField(required=False)
    participants = ListField(ReferenceField(UserLoginInfo), default=list)


class MessageRecipients(EmbeddedDocument):
    is_received = ListField(ReferenceField(UserLoginInfo), default=list)
    is_read = ListField(ReferenceField(UserLoginInfo), default=list)
    room = ReferenceField(ChatRoom)


class MessageMedia(EmbeddedDocument):
    link = URLField(required=False)
    caption = StringField(required=False)


class Message(AbstractBaseModel):
    sender = ReferenceField(UserLoginInfo)
    type = StringField(choices=MESSAGE_TYPES, default=DEFAULT_MESSAGE_TYPE, required=True)
    message_body = MultiLineStringField(required=True)
    message_media = EmbeddedDocumentField(MessageMedia)
    is_sent = BooleanField(default=False)
    recipients = EmbeddedDocumentListField(MessageRecipients)
