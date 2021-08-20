import datetime
import json
import os
from base64 import b64encode
import razorpay
import requests

client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY'), os.environ.get('IHJtyvJRYdQhJ6ZynkQxug05')))

basic_auth_client = b64encode(
    "{}:{}".format(os.environ.get('RAZORPAY_KEY'), os.environ.get('RAZORPAY_SECRET')).encode()).decode("ascii")


def razorpay_create_customer(name, email, phone, gstin='', notes=None):
    if notes is None:
        notes = {}
    error = False
    data = {
        "name": name,
        "email": email,
        "contact": phone,
        "fail_existing": "1",
        "gstin": gstin,
        "notes": notes
        # "notes": {
        #     "notes_key_1": "Tea, Earl Grey, Hot",
        #     "notes_key_2": "Tea, Earl Grey… decaf."
        # }
    }
    try:
        response = client.customer.create(data=data)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_get_customer(customer_id):
    error = False
    try:
        response = client.customer.fetch(customer_id=customer_id)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_edit_customer(customer_id, name, email, phone, gstin='', notes=None):
    if notes is None:
        notes = {}
    error = False
    data = {
        "name": name,
        "email": email,
        "contact": phone,
        "fail_existing": "1",
        "gstin": gstin,
        "notes": notes
        # "notes": {
        #     "notes_key_1": "Tea, Earl Grey, Hot",
        #     "notes_key_2": "Tea, Earl Grey… decaf."
        # }
    }
    try:
        response = client.customer.edit(customer_id=customer_id, data=data)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_create_order(amount, currency, receipt='None', notes=''):
    error = False
    try:
        data = {
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'notes': notes
        }
        response = client.order.create(data=data)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_create_payment_link(amount, currency, description='', customer_name='', customer_email='', customer_phone='',
                        notes=None, callback_url='', callback_method='get'):
    if notes is None:
        notes = {}

    expiry = datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(hours=6))
    error = False
    url = "https://api.razorpay.com/v1/payment_links"

    payload = {'amount': int(amount), 'currency': currency, 'accept_partial': False,
               'description': description, 'expire_by': int(expiry),
               'customer': {'name': customer_name, 'contact': customer_phone, 'email': customer_email},
               'notify': {'sms': True, 'email': True}, 'reminder_enable': True, 'notes': notes,
               'callback_url': callback_url, 'callback_method': callback_method}

    headers = {
        'Authorization': f'Basic {basic_auth_client}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    print(response.text)
    try:
        response_data = response.json()
    except:
        response_data = response.text
        error = True
    return error, response_data


def razorpay_capture_payment(payment_id, amount, currency):
    error = False
    try:
        response = client.payment.capture(payment_id, amount, {"currency": currency})
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_get_payment(payment_id):
    error = False
    try:
        response = client.payment.fetch(payment_id)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_generate_refund(payment_id, amount):
    error = False
    try:
        response = client.payment.refund(payment_id, amount)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response


def razorpay_get_refund(refund_id):
    error = False
    try:
        response = client.refund.fetch(refund_id)
    except Exception as e:
        print(e)
        error = True
        response = str(e)
    return error, response
