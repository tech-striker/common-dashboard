# flask packages
from flask import request, jsonify
from flask_restful import Resource
from authentication.services import create_user
from authentication.selectors import login_user, social_login, update_user
from flask import Response
from utils.common import generate_response
from authentication.models import UserLoginInfo
from utils.http_code import *
from utils.common import account_activation_token
from utils.common import get_user_from_token
from utils.jwt.jwt_security import authenticate_login


class SignUpApi(Resource):

    @staticmethod
    def post() -> Response:
        """
        POST response method for creating user.

        :return: JSON object
        """
        input_data = request.get_json()
        response = create_user(request, input_data)
        return jsonify(response)


class EmailLoginApi(Resource):

    @staticmethod
    def post() -> Response:
        """
        POST response method for retrieving user web token.

        :return: JSON object
        """
        input_data = request.get_json()
        response = login_user(request, input_data)
        return jsonify(response)


class SocialLoginApi(Resource):

    @staticmethod
    def post() -> Response:
        """
        POST response method for retrieving user web token.

        :return: JSON object
        """
        input_data = request.get_json()
        response = social_login(request, input_data)
        return jsonify(response)


class VerifyUserApi(Resource):

    @staticmethod
    def get(uid, token):
        try:
            user = UserLoginInfo.objects.get(id=uid)
        except:
            user = None
        if user is not None and account_activation_token.check_token(token):
            user.is_verified = True
            user.save()

            return 'Thank you for your email confirmation. Now you can login your account.'
        else:
            return 'Activation link is invalid!'


class UserProfileApi(Resource):
    @staticmethod
    @authenticate_login
    def get() -> Response:
        jwt_payload = get_user_from_token(request)
        user = UserLoginInfo.objects(id=jwt_payload['id']).exclude('password').get()
        return jsonify(generate_response(data=user, status=HTTP_404_NOT_FOUND))

    @staticmethod
    @authenticate_login
    def delete() -> Response:

        jwt_payload = get_user_from_token(request)
        user = UserLoginInfo.objects.get(id=jwt_payload['id'])
        user.is_deleted = True
        user.save()
        return jsonify(generate_response(data=user.to_json()['id'], message='User deleted.', status=HTTP_404_NOT_FOUND))

    @staticmethod
    @authenticate_login
    def put() -> Response:
        input_data = request.get_json()
        jwt_payload = get_user_from_token(request)
        user = UserLoginInfo.objects.get(id=jwt_payload['id'])
        response = update_user(input_data, user)
        return jsonify(response)


def ChatApi():
    pass
