import string
from datetime import datetime

from socketsio import socketio
from app import app
from chat.models import ChatRoom, MessageRecipients, MessageMedia, Message
from utils.common import generate_response
from utils.http_code import *
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from utils.common import get_user_from_token
from chat.selectors import get_rooms
from app import session
from flask import request
from utils.services.email_service import send_chat_notification


@socketio.on('connected')
def connect(data):
    if not check_if_sid_exists(data):
        session.chat_clients[data['sid']] = {
            'sid': request.sid,
            'user': get_user_from_token(token=data['token'])
        }


@socketio.on('disconnect')
def disconnect():
    del (session.chat_clients[request.sid])


def check_if_sid_exists(data):
    try:
        sid = session.chat_clients[data['sid']]
        return True
    except:
        return False


@socketio.on('get_chats')
def get_chats(data):
    user = get_user_from_token(token=data['token'])
    chats = get_rooms(data, user['id'])
    # callable({
    #     'chats': [chat.to_json() for chat in chats]
    # })
    emit('set_chats', {'chats': [chat.to_json() for chat in chats]})


# @socketio.on("confirm login")
# def confirm_login(data):
#     print(data)
#     print('Confirm Login')
#     """ If the user connects with the local storage login method, ensure that
#         the 'users' list is updated in the server.
#     """
#     username = data["username"]
#     if username not in users:
#         users.append(username)
#         app.logger.info(f"Appended username: '{username}'")
#     app.logger.info("Confirmed login.")
#
#
# @socketio.on("user logged in")
# def log_in(data):
#     print(data)
#     print('Inside User Loggedin')
#     """ Adds username to the server list of users. This is for
#         form-submitted data.
#     """
#     username = data["username"]
#     if username not in users:
#         users.append(username)
#         # app.logger.info(f"\nLogging {username} in. Users: \n{users}")
#         emit("new user",
#              {"username": username}, broadcast=False)
#     else:
#         app.logger.info(f"Username '{username}' taken.")
#         emit("username taken", broadcast=False)

from authentication.models import UserLoginInfo


@socketio.on("new_room_create")
def create_new_channel(data):
    print(data)
    print('New channel')
    """ Checks whether a channel can be created. If so, this updates the
        channel list and broadcasts the new channel.
    """
    # channel = clean_up_channel_name(data["channel"])
    from utils.common import get_user_from_token
    user = get_user_from_token(token=data['Authorization'])
    error = validate_room(data, user['id'])
    if error:
        emit("room_creation_failed", error, broadcast=False)
    from utils.common import get_user_from_token
    # user = get_user_from_token(token=data['Authorization'] if 'Authorization' in data else '61010e5289d57973f9010b04')
    chat_room = ChatRoom(name=data['name'] if 'name' in data else '')
    chat_room.creator = UserLoginInfo.objects.get(id=user['id'])
    chat_room.is_group = data['is_group'] if 'is_group' in data else True
    chat_room.save()
    admins = UserLoginInfo.objects.get(id=user['id'])
    chat_room.name = data['name']
    chat_room.admins = [admins]
    participant_ids = data['participants'] if 'participants' else []
    participants = [admins]
    for participant in participant_ids:
        participants.append(UserLoginInfo.objects.get(id=participant))
    chat_room.participants = participants
    chat_room.save()
    join_room(str(chat_room.id))
    emit("add_room", {"channel": chat_room.to_json()}, broadcast=True)


# @socketio.on("move to channel")
# def move_user_to_room(data):
#     print(data)
#     print('Move user')
#     """ Moves the user to the specified channel. Checks to see if the channel
#         exists in the server list of channels.
#     """
#     channel = data["channel"]
#     messages = messages_dict[channel]
#     if channel in channels:
#         emit("enter channel room", {"channel": channel, "messages": messages})


@socketio.on("new_message")
def new_message(data):
    print(data)
    print('New Message Loggedin')
    """ Processes the new message and stores it into the server list of
        messages given the room name. Broadcast the room and message.
    """
    errors = validate_message(data)
    if errors:
        emit("message_failed", errors, broadcast=False)
    timestamp = get_timestamp_trunc()
    user = get_user_from_token(token=data['token'])
    sender = UserLoginInfo.objects.get(id=user['id'])
    room_data = ChatRoom.objects.get(id=data['room'])
    recipients = []
    for participant in room_data.participants:
        message_recipients = MessageRecipients(recipient=participant)
        message_recipients.room = room_data
        recipients.append(message_recipients)

    message = Message(sender=sender)
    message.type = data['type']
    message.message_body = data['message_body']
    message.recipients = recipients
    message.save()

    data = {
        "room": data['room'],
        "message_body": message.to_json(),
        "timestamp": timestamp,
        "sender": sender.to_json()
    }
    # import pdb;
    # pdb.set_trace()
    # clients = get_chat_clients(room_data)
    try:
        send_email_notification(room_data, message.message_body, user.email)
    except Exception as e:
        print(e)

    emit("message_broadcast", data, broadcast=True)


def send_email_notification(room_data, message_body, sender_email):
    recipient_emails = list
    for participant in room_data.participants:
        is_user_found = False
        for key, value in session.chat_clients.items():
            if str(participant.id) == value['user']['id']:
                is_user_found = True
        if not is_user_found:
            recipient_emails.append(participant.email)
    send_chat_notification(recipient_emails, message_body, sender_email)


def get_chat_clients(room_data):
    clients = []
    for participant in room_data.participants:
        for key, value in session.chat_clients.items():
            if str(participant.id) == value['user']['id']:
                clients.append(key)

    return clients


# @socketio.on("verify channel")
# def verify_channel(data):
#     print(data)
#     print('Verify Channel')
#     """ Verifies whether the channel exists or not.
#     """
#     channel = data["channel"]
#     if channel not in channels:
#         emit("default channel")
#     else:
#         # do nothing if the channel exists
#         pass


def get_timestamp_trunc():
    """ Grabs the timestamp rounds the decimal point to deciseconds.
        For example:
        '2019-07-04 00:18:39.532357' becomes
        '2019-07-04 00:18:39.5'
    """
    timestamp = str(datetime.now())
    return timestamp[:-5]


def validate_room(data, user_id):
    if 'participants' not in data or not type(data['participants']) is list:
        return generate_response(message='invalid participants', status=HTTP_400_BAD_REQUEST)
    if 'is_group' in data:
        if data['is_group']:
            if 'name' not in data or not data['name']:
                return generate_response(message='Group name is required', status=HTTP_400_BAD_REQUEST)
            if ChatRoom.objects(name=data['name']):
                return generate_response(message='Group with this name is already exists', status=HTTP_400_BAD_REQUEST)
        else:
            chat_room = ChatRoom.objects(participants__in=[user_id['id'], data['participants'][0]])
            if chat_room:
                return generate_response(data=chat_room[0].to_json(), status=HTTP_200_OK)

    return None


def validate_message(data):
    if 'token' not in data or not data['token']:
        return generate_response(message='token is required', status=HTTP_400_BAD_REQUEST)
    if 'room' not in data or not data['room']:
        return generate_response(message='room is required', status=HTTP_400_BAD_REQUEST)
    if 'message_body' not in data or not data['message_body']:
        return generate_response(message='message_body is required', status=HTTP_400_BAD_REQUEST)
    if 'type' not in data or not data['type']:
        return generate_response(message='type is required', status=HTTP_400_BAD_REQUEST)
    return None


def clean_up_channel_name(text: str) -> str:
    """ Clean up extra spaces and remove punctuation from channel name.
    """
    # Remove punctuation
    text = text.strip().translate(str.maketrans('', '', string.punctuation))

    # Remove extra spaces by splitting spaces and rejoining
    text = ' '.join(text.split())

    return text


def valid_channel(channel: str) -> bool:
    """ Checks whether the channel is a valid channel name.
    """
    if channel == "":
        return False
    return True
