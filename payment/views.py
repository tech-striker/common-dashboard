from flask import render_template, make_response
from flask_restful import Resource
from flask import request, jsonify
from utils.common import get_user_from_token, generate_response
from utils.jwt.jwt_security import authenticate_login
from .selectors import get_cards, get_invoices, get_refunds
from .services import create_card, validate_card_input_data, delete_card, validate_payment_input_data, create_payment, \
    validate_refund_input_data, create_refund, generate_refund, cancel_refund
from utils.http_code import *
from payment.stripe import stripe_webhook


class CardApi(Resource):
    @staticmethod
    @authenticate_login
    def get():
        user = get_user_from_token(request)
        cards = get_cards(user['id'])
        return jsonify(generate_response(data=cards, status=HTTP_404_NOT_FOUND))

    @staticmethod
    @authenticate_login
    def post():
        input_data = request.get_json()
        user = get_user_from_token(request)
        error = validate_card_input_data(input_data)
        if error:
            return error
        response = create_card(input_data, user['id'])
        return jsonify(response)

    @staticmethod
    @authenticate_login
    def delete():
        input_data = request.get_json()
        if 'id' not in input_data or not input_data['id']:
            return generate_response(message='Card Id is required.')
        response = delete_card(input_data['id'])
        return jsonify(response)


class PaymentApi(Resource):
    @staticmethod
    @authenticate_login
    def get():
        user = get_user_from_token(request)
        invoices = get_invoices(user['id'])
        return jsonify(generate_response(data=invoices, status=HTTP_404_NOT_FOUND))

    @staticmethod
    @authenticate_login
    def post():
        input_data = request.get_json()
        user = get_user_from_token(request)
        error = validate_payment_input_data(input_data)
        if error:
            return error
        response = create_payment(input_data, user['id'])
        return jsonify(response)


class RefundApi(Resource):
    @staticmethod
    @authenticate_login
    def get():
        refunds = get_refunds()
        return jsonify(generate_response(data=refunds, status=HTTP_404_NOT_FOUND))

    @staticmethod
    @authenticate_login
    def post():
        input_data = request.get_json()
        user = get_user_from_token(request)
        error = validate_refund_input_data(input_data)
        if error:
            return error
        response = create_refund(input_data)
        return jsonify(response)


class GenerateRefundApi(Resource):
    @staticmethod
    @authenticate_login
    def get(payment_id):
        user = get_user_from_token(request)
        if user['role'] != 'SUPER_ADMIN':
            return jsonify(generate_response(
                message='You are not allowed to perform this action. this action can be done by super admin only'))
        response = generate_refund(payment_id)
        # from socketsio.payment_events import emit_generate_refund_event
        # emit_generate_refund_event(response)
        return jsonify(response)


class CancelRefundApi(Resource):
    @staticmethod
    @authenticate_login
    def post():
        input_data = request.get_json()
        user = get_user_from_token(request)
        response = cancel_refund(input_data, user)
        return jsonify(response)


class StripeWebhookApi(Resource):
    @staticmethod
    def post():
        try:
            stripe_webhook(request)
        except:pass
        return 200
