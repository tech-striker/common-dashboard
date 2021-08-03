from payment.models import Card, Payment, PaymentCustomer


def get_cards(user_id):
    cards = Card.objects(user=user_id).to_json()
    return cards


def get_invoices(user_id):
    invoices = Payment.objects(user=user_id).to_json()
    return invoices
