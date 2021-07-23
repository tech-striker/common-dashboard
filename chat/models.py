from mongoengine import *
from utils.constants import *
from utils.db.base_model import AbstractBaseModel
from authentication.models import UserLoginInfo


class Group(AbstractBaseModel):
    admin = ReferenceField(UserLoginInfo, )
    name = StringField(required=True)
    is_active = BooleanField(default=True)
    participants = ListField(ReferenceField(UserLoginInfo))


class MessageRecipient(AbstractBaseModel):
    recipient = ReferenceField(UserLoginInfo)
    recipient_group = ReferenceField(Group)
    is_read = BooleanField(default=False)


class Message(AbstractBaseModel):
    sender = ReferenceField(UserLoginInfo)
    message_body = MultiLineStringField(required=True)
    type = StringField(choices=MESSAGE_TYPES, default=DEFAULT_MESSAGE_TYPE, required=True)
    is_sent = BooleanField(default=False)
    is_received = BooleanField(default=False)
    is_read = BooleanField(default=False)
