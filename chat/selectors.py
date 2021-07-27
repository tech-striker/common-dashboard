from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
import datetime
import random
from utils.jwt.jwt_security import JwtAuth
import os
from .models import MessageMedia, MessageRecipients, Message, ChatRoom


def get_channels(input_data):
    try:
        rooms = ChatRoom.objects(participants__in=input_data['user_id'])
    except:
        rooms = ChatRoom.objects.all()
    return rooms
