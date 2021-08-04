from payment.models import Card, PaymentCustomer, Payment
from .stripe import stripe_card_create, stripe_token_create, create_stripe_customer, create_stripe_charge
from utils.common import generate_response
from utils.http_code import *


def create_card(input_data, user_id):
    customer = PaymentCustomer.objects(user=user_id).last()
    token = stripe_token_create(input_data['card_number'], input_data['exp_month'], input_data['exp_year'],
                                input_data['cvv'])
    if not token:
        return generate_response(message='Error with creating card, please contact your bank.')
    card_data = stripe_card_create(customer_id=customer.id, token_id=token.id)
    if not card_data:
        return generate_response(message='Error with creating card, please contact your bank.')
    card = Card(user=user_id)
    card.last_4 = input_data['last_4']
    card.stripe_card_id = card_data.id
    card.card_type = card_data.type
    card.is_primary = input_data['is_primary'] if 'is_primary' in input_data else False
    card.save()
    return generate_response(message='Card successfully created.', data=card.id, status=HTTP_200_OK)


def delete_card(card_id):
    card = Card.objects(id=card_id).delete()
    return generate_response(message='Card is deleted successfully', status=HTTP_200_OK)


def create_payment_customer(user):
    customer_data = create_stripe_customer(user.name, user.email, user.phone)
    customer = PaymentCustomer(user=user.id)
    customer.customer_id = customer_data.id
    customer.save()


def create_payment(input_data, user_id):
    customer = PaymentCustomer.objects(user=user_id)
    payment_data = create_stripe_charge(input_data['amount'], input_data['currency'], input_data['card'],
                                        customer.customer_id)
    if not payment_data:
        return generate_response(message='Error from payment. please check your card.')
    payment = Payment(user=user_id)
    payment.order = input_data['order']
    payment.card = input_data['card']
    payment.amount = input_data['amount']
    payment.currency = input_data['currency']
    payment.payment_id = payment_data.id
    payment.save()
    return generate_response(message='Payment initiated please wait to complete.', status=HTTP_200_OK)


def validate_card_input_data(input_data):
    if 'card_number' not in input_data or not input_data['card_number']:
        return generate_response(message='Card Number is required')
    if 'exp_month' not in input_data or not input_data['exp_month']:
        return generate_response(message='Expiry Month is required')
    if 'exp_year' not in input_data or not input_data['exp_year']:
        return generate_response(message='Expiry Year is required')
    if 'cvv' not in input_data or not input_data['cvv']:
        return generate_response(message='CVV is required')

    return None


def validate_payment_input_data(input_data):
    if 'order' not in input_data or not input_data['order']:
        return generate_response(message='Order Id is required')
    if 'card' not in input_data or not input_data['card']:
        return generate_response(message='Card Id is required')
    if 'amount' not in input_data or not input_data['amount']:
        return generate_response(message='Total amount is required')
    if 'currency' not in input_data or not input_data['currency']:
        return generate_response(message='Currency is required')

    return None
