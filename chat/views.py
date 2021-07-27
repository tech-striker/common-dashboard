from flask import render_template, make_response
from flask_restful import Resource
from flask import request, jsonify
from .selectors import get_rooms


class ChatApi(Resource):

    @staticmethod
    def get():
        import pdb;
        pdb.set_trace()
        input_data = request.values.to_dict()
        user_id = '3deef3340e1340fe9eb426ba46cb4c46'
        rooms = get_rooms(input_data, user_id)
        return make_response(render_template("index.html",
                                             # users=users,
                                             channels=rooms))
