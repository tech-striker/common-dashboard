from payment.models import CardModel, PaymentModel, PaymentCustomerModel, RefundModel, ShippingAddressModel
import json
from utils.common import generate_response
from utils.http_code import *


def get_cards(user_id):
    cards = [card.to_json() for card in CardModel.objects(user=user_id)]
    return cards


def get_invoices(user_id):
    invoices = [payment.to_json() for payment in PaymentModel.objects(user=user_id)]
    return invoices


def get_refunds():
    refunds = [refund.to_json() for refund in RefundModel.objects()]
    return refunds


def get_user_location(jwt_payload, input_data):
    if 'id' in input_data:
        location = ShippingAddressModel.objects(id=input_data['id']).get().to_json()
    else:
        location = [loc.to_json() for loc in ShippingAddressModel.objects.filter(user=jwt_payload['id'])]
    return generate_response(data=location, status=HTTP_200_OK)
