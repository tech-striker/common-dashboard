import os

import stripe

try:
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
except:
    stripe.api_key = ""
    print("STRIPE_SECRET_KEY not available.STRIPE_SECRET_KEY needs to be set in environment file.")


def create_stripe_customer(name, email, phone):
    try:
        params = {'name': name, 'email': email, 'phone': phone, "address": {
            'line1': '510 Townsend St',
            'postal_code': '98140',
            'city': 'San Francisco',
            'state': 'CA',
            'country': 'US', }, }
        response = stripe.Customer.create(**params)
        return response
    except Exception as e:
        print('Error creating stripe customer: %s', e.__str__())
        return None


def stripe_token_create(card_number, exp_month, exp_year, cvc):
    response = None
    try:
        response = stripe.Token.create(
            card={
                "number": str(card_number),
                "exp_month": int(exp_month),
                "exp_year": int(exp_year),
                "cvc": str(cvc),
            })
    except Exception as e:
        print(e.__str__())
    return response


def stripe_card_create(customer_id, token_id):
    response = None
    try:
        response = stripe.Customer.create_source(
            customer_id,
            source=token_id)
    except Exception as e:
        print(e.__str__())
    return response


def create_stripe_charge(amount, currency, source_id, customer_id):
    response = None
    # import pdb;pdb.set_trace()
    try:
        response = stripe.Charge.create(
            amount=int(amount) * 100,
            currency=str(currency).lower(),
            source=source_id,
            customer=customer_id,
            description="My First Test Charge (created for API docs)",
            shipping={
                "address": {
                    "line1": "16-A"
                },
                "name": "John vick"
            }
        )
    except Exception as e:
        print(e.__str__())
    return response


def refund_stripe_charge(payment_id=None):
    response = None
    try:
        response = stripe.Refund.create(
            charge=payment_id,
        )
    except Exception as e:
        print(e.__str__())
        response = None
    return response
