from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
import datetime
import random
from utils.jwt.jwt_security import JwtAuth
import os
from .models import MessageMedia, MessageRecipients, Message, ChatRoom


def get_rooms(input_data, user_id):
    try:
        rooms = ChatRoom.objects(participants__in=user_id)
    except:
        rooms = ChatRoom.objects.all()

    for room in rooms:
        if not room.is_group:
            if user_id == room.participants[0].id:
                room.name = room.participants[-1].name
            else:
                room.name = room.participants[0].name
    return rooms
