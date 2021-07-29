from flask import render_template, make_response
from flask_restful import Resource
from flask import request, jsonify
from .selectors import get_rooms, get_messages
from utils.common import get_user_from_token


class ChatApi(Resource):

    @staticmethod
    def get():
        input_data = request.values.to_dict()
        # user_id = '61010e5289d57973f9010b04'
        # rooms = get_rooms(input_data, user_id)
        return make_response(render_template("index.html",
                                             # users=users,
                                             channels=[]))


class MessageApi(Resource):

    @staticmethod
    def get():
        input_data = request.values.to_dict()
        response = get_messages(input_data)
        return jsonify(response)
