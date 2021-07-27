# flask packages
from flask_restful import Api

# project resources
from chat.views import ChatApi

import os
import string
from datetime import datetime

from flask import render_template, make_response
from flask_socketio import SocketIO, emit
from flask import request, jsonify
from flask_restful import Resource
from app import app

users = []  # list of users
channels = ["Main Channel", "Second Channel"]  # list of channels

# Dictionary of list of dictionaries
# Contains channel -> messages -> (text, username, AND timestamp)
messages_dict = {
    "Main Channel": [
        {
            "message": "Welcome, friends!",
            "username": "Tbone",
            "timestamp": "2019-04-07"
        },
        {
            "message": "Hi, nice to meet you :)!",
            "username": "Georgie",
            "timestamp": "2019-04-07"
        }],
    "Second Channel": [
        {
            "message": "hello!",
            "username": "random_person_123",
            "timestamp": "2019-03-06"
        }
    ]
}
message_limit = 100


def create_chat_routes(api: Api):
    """Adds resources to the api.

    :param api: Flask-RESTful Api Object

    :Example:

        api.add_resource(HelloWorld, '/', '/hello')
        api.add_resource(Foo, '/foo', endpoint="foo")
        api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

    """
    api.add_resource(ChatApi, '/chat/')
