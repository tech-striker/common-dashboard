from flask import render_template, make_response
from flask_restful import Resource
from flask import request, jsonify
from .selectors import get_channels


class ChatApi(Resource):

    @staticmethod
    def get():
        import pdb;pdb.set_trace()
        input_data = request.values.to_dict()
        rooms = get_channels(input_data)
        return make_response(render_template("index.html",
                                             # users=users,
                                             channels=rooms))
