import json

from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
import datetime
import random
from utils.jwt.jwt_security import JwtAuth
import os

from .models import MessageMedia, MessageRecipients, Message, ChatRoom


def get_rooms(input_data, user_id):
    rooms = ChatRoom.objects.select_related(3)

    for room in rooms:
        if not room['is_group']:
            if room['participants']:
                if user_id == room['participants'][0].to_json()['id']:
                    room['name'] = room['participants'][-1].to_json()['email']
                else:
                    room['name'] = room['participants'][0].to_json()['email']
    return rooms


def get_messages(input_data):
    messages = Message.objects(recipients__room=input_data['room'])
    return generate_response(data={'room': input_data['room'], 'messages': [message.to_json() for message in messages]},
                             status=HTTP_200_OK)
