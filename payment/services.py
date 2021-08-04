from payment.models import CardModel, PaymentCustomerModel, PaymentModel, RefundModel
from .stripe import stripe_card_create, stripe_token_create, create_stripe_customer, create_stripe_charge, \
    refund_stripe_charge
from utils.common import generate_response
from utils.http_code import *
from utils.constants import REFUND_GENERATED, REFUND_CANCELED
from payment.models import CardModel


def create_card(input_data, user_id):
    customer = PaymentCustomerModel.objects(user=user_id).first()
    token = stripe_token_create(input_data['card_number'], input_data['exp_month'], input_data['exp_year'],
                                input_data['cvv'])
    if not token:
        return generate_response(message='Error with creating card, please contact your bank.')
    card_data = stripe_card_create(customer_id=customer.customer_id, token_id=token.id)
    if not card_data:
        return generate_response(message='Error with creating card, please contact your bank.')
    card = CardModel(user=user_id)
    card.last_4 = card_data['last4']
    card.stripe_card_id = card_data['id']
    card.card_type = card_data['brand']
    card.is_primary = input_data['is_primary'] if 'is_primary' in input_data else False
    card.save()
    return generate_response(message='Card successfully created.', data=card.to_json()['id'], status=HTTP_200_OK)


def delete_card(card_id):
    card = CardModel.objects(id=card_id).delete()
    return generate_response(message='Card is deleted successfully', status=HTTP_200_OK)


def create_payment_customer(user):
    import pdb;pdb.set_trace()
    customer_data = create_stripe_customer(user.name, user.email, user.phone)
    customer = PaymentCustomerModel(user=user.id)
    customer.customer_id = customer_data['id']
    customer.save()


def create_payment(input_data, user_id):
    import pdb;pdb.set_trace()
    customer = PaymentCustomerModel.objects(user=user_id).get()
    card_data = CardModel.objects(id=input_data['card']).get()
    payment_data = create_stripe_charge(input_data['amount'], input_data['currency'], card_data['stripe_card_id'],
                                        customer.customer_id)
    if not payment_data:
        return generate_response(message='Error from payment. please check your card.')
    payment = PaymentModel(user=user_id)
    payment.order = input_data['order']
    payment.card = card_data.id
    payment.amount = input_data['amount']
    payment.currency = input_data['currency']
    payment.payment_id = payment_data['id']
    payment.save()
    return generate_response(message='Payment initiated please wait to complete.', data=str(payment.id), status=HTTP_200_OK)


def create_refund(input_data):
    refund = RefundModel(payment=input_data['payment_id'])
    refund.refund_reason = input_data['refund_reason'] if 'refund_reason' in input_data else ''
    refund.save()
    return generate_response(
        message='Your refund request is sent to the admin, refund process can take 5-6 business days. please wait.',
        status=HTTP_200_OK)


def generate_refund(payment_id):
    refund_data = refund_stripe_charge(payment_id)
    if not refund_data:
        return generate_response(message='Refund not generated, please check you account balance.')
    refund = RefundModel.objects(payment=payment_id)
    refund.status = REFUND_GENERATED
    refund.save()
    return generate_response(message='Refund generated successful', status=HTTP_200_OK)


def cancel_refund(input_data, user):
    if user['role'] != 'SUPER_ADMIN':
        return generate_response(
            message='You are not allowed to perform this action. this action can be done by super admin only')
    if 'payment_id' not in input_data or not input_data['payment_id']:
        return generate_response(message='payment_id is required')
    if 'refund_cancellation_reason' not in input_data or not input_data['refund_cancellation_reason']:
        return generate_response(message='refund_cancellation_reason is required')
    refund = RefundModel.objects(payment=input_data['payment_id'])
    refund.status = REFUND_CANCELED
    refund.refund_cancellation_reason = input_data['refund_cancellation_reason']
    refund.save()
    return generate_response(message='Refund generated successful', status=HTTP_200_OK)


def validate_card_input_data(input_data):
    if 'card_number' not in input_data or not input_data['card_number']:
        return generate_response(message='Card Number is required')
    if 'exp_month' not in input_data or not input_data['exp_month']:
        return generate_response(message='Expiry Month is required')
    if 'exp_year' not in input_data or not input_data['exp_year']:
        return generate_response(message='Expiry Year is required')
    if 'cvv' not in input_data or not input_data['cvv']:
        return generate_response(message='CVV is required')
    if CardModel.objects(card_number=input_data['card_number']):
        return generate_response(message='This card is already saved in our records.')

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


def validate_refund_input_data(input_data):
    if 'payment_id' not in input_data or not input_data['payment_id']:
        return generate_response(message='payment_id is required')
    if 'refund_reason' not in input_data:
        return generate_response(message='refund_reason is required')
    return None
