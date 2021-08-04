from payment.models import CardModel, PaymentModel, PaymentCustomerModel, RefundModel
import json


def get_cards(user_id):
    cards = [card.to_json() for card in CardModel.objects(user=user_id)]
    return cards


def get_invoices(user_id):
    invoices = [payment.to_json() for payment in PaymentModel.objects(user=user_id)]
    return invoices


def get_refunds():
    refunds = [refund.to_json() for refund in RefundModel.objects()]
    return refunds
