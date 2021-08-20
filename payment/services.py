import os

from payment.models import CardModel, PaymentCustomerModel, PaymentModel, RefundModel
from .stripe import stripe_card_create, stripe_token_create, create_stripe_customer, create_stripe_charge, \
    refund_stripe_charge
from .razorpay import razorpay_create_customer, razorpay_create_order, razorpay_create_payment_link, \
    razorpay_capture_payment, razorpay_generate_refund
from utils.common import generate_response
from utils.http_code import *
from utils.constants import REFUND_GENERATED, REFUND_CANCELED
from payment.models import CardModel
from utils.constants import *


def stripe_create_card(input_data, user_id):
    customer = PaymentCustomerModel.objects(user=user_id, payment_gateway=STRIPE_GATEWAY).first()
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


def stripe_delete_card(card_id):
    card = CardModel.objects(id=card_id).delete()
    return generate_response(message='Card is deleted successfully', status=HTTP_200_OK)


def stripe_create_payment_customer(user):
    customer_data = create_stripe_customer(user['name'], user['email'], user['phone'])
    customer = PaymentCustomerModel(user=user['id'])
    customer.customer_id = customer_data['id']
    customer.payment_gateway = STRIPE_GATEWAY
    customer.save()
    return customer.to_json()


def stripe_create_payment(input_data, user):
    try:
        customer = PaymentCustomerModel.objects(user=user['id'], payment_gateway=STRIPE_GATEWAY).get()
    except:
        customer = stripe_create_payment_customer(user)
    card_data = CardModel.objects(id=input_data['card']).get()
    payment_data = create_stripe_charge(input_data['amount'], input_data['currency'], card_data['stripe_card_id'],
                                        customer.customer_id)
    if not payment_data:
        return generate_response(message='Error from payment. please check your card.')
    payment = PaymentModel(user=user['id'])
    payment.order = input_data['order']
    payment.card = card_data.id
    payment.amount = input_data['amount']
    payment.currency = input_data['currency']
    payment.payment_id = payment_data['id']
    payment.payment_gateway = STRIPE_GATEWAY
    payment.save()
    return generate_response(message='Payment initiated please wait to complete.', data=str(payment.id),
                             status=HTTP_200_OK)


def create_refund(input_data):
    refund = RefundModel(payment=input_data['payment_id'])
    refund.refund_reason = input_data['refund_reason'] if 'refund_reason' in input_data else ''
    refund.save()
    return generate_response(
        message='Your refund request is sent to the admin, refund process can take 5-6 business days. please wait.',
        status=HTTP_200_OK)


def stripe_generate_refund(payment_id):
    payment = PaymentModel.objects(payment_id=payment_id).get()
    refund_data = refund_stripe_charge(payment_id)
    if not refund_data:
        return generate_response(message='Refund not generated, please check you account balance.')
    refund = RefundModel.objects(payment=payment_id)
    refund.status = REFUND_GENERATED
    refund.save()
    payment.status = PAYMENT_REFUNDED
    payment.save()
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


def razorpay_create_payment(request, input_data, user):
    # try:
    #     customer = PaymentCustomerModel.objects(user=user['id'], payment_gateway=STRIPE_GATEWAY).get()
    # except:
    #     customer = stripe_create_payment_customer(user)
    error, payment_response = razorpay_create_payment_link(
        amount=input_data['amount'], currency=input_data['currency'],
        customer_name=user['name'], customer_email=user['email'],
        customer_phone=user['phone'],
        callback_url=request.url_root + 'api/payment/razorpay/capture-payment/',
        callback_method='get'
    )
    if error:
        return generate_response(message='Error from payment. please check your card.', data=payment_response)
    payment = PaymentModel(user=user['id'])
    payment.order = input_data['order']
    payment.amount = input_data['amount']
    payment.currency = input_data['currency']
    payment.status = PAYMENT_INITIATED
    payment.payment_gateway = RAZORPAY_GATEWAY
    payment.payment_link_ref_id = payment_response['id']
    payment.save()
    data = {
        'id': str(payment.id),
        'payment_id': payment_response['id'],
        'payment_url': payment_response['short_url'],
    }
    return generate_response(message='Payment link created please click on this link to make payment.',
                             data=data,
                             status=HTTP_200_OK)


def capture_razorpay_payment(payment_link_ref_id, payment_id):
    payment = PaymentModel.objects(payment_link_ref_id=payment_link_ref_id).first()
    # error, payment_response = razorpay_capture_payment(payment_id, payment.amount, payment.currency)
    # if error:
    #     return generate_response(message='Error from payment. please check your card.', data=payment_response)
    payment.status = PAYMENT_SUCCESS
    payment.save()
    return generate_response(message='Payment pending please wait to complete.', data=str(payment.id),
                             status=HTTP_200_OK)


def generate_razorpay_refund(payment_id):
    payment = PaymentModel.objects(payment_id=payment_id).get()
    refund_data = razorpay_generate_refund(payment_id, payment.amount)
    if not refund_data:
        return generate_response(message='Refund not generated, please check you account balance.')
    refund = RefundModel.objects(payment=payment_id)
    refund.status = REFUND_GENERATED
    refund.save()
    payment.status = PAYMENT_REFUNDED
    payment.save()
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


def validate_stripe_payment_input_data(input_data):
    if 'order' not in input_data or not input_data['order']:
        return generate_response(message='Order Id is required')
    if 'card' not in input_data or not input_data['card']:
        return generate_response(message='Card Id is required')
    if 'amount' not in input_data or not input_data['amount']:
        return generate_response(message='Total amount is required')
    if 'currency' not in input_data or not input_data['currency']:
        return generate_response(message='Currency is required')

    return None


def validate_razorpay_payment_input_data(input_data):
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
