import os

import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.environ.get('BRAINTREE_MERCHANT_ID'),
        public_key=os.environ.get('BRAINTREE_PUBLIC_KEY'),
        private_key=os.environ.get('BRAINTREE_PRIVATE_KEY')
    )
)


def create_braintree_customer(first_name='', last_name='', comapny='', email='', phone='', website=''):
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "company": comapny,
        "email": email,
        "phone": phone,
        "website": website
    }
    error = False
    result = gateway.customer.create(data)
    result = result.customer.id
    if not result.is_success:
        error = True
        result = result.message
    return error, result


def generate_braintree_token(customer_id):
    data = {
        "customer_id": customer_id
    }
    error = False
    result = gateway.customer.create(data)
    result = result.token
    if not result.is_success:
        error = True
        result = result.message
    return error, result


def generate_braintree_payment_method_nonce(token):
    error = False
    result = gateway.payment_method_nonce.create(token)
    result = result.payment_method_nonce.nonce
    if not result.is_success:
        error = True
        result = result.message
    return error, result


def generate_braintree_payment_method_nonce(customer_id, payment_method_nonce):
    error = False
    result = gateway.payment_method.create({
        "customer_id": customer_id,
        "payment_method_nonce": payment_method_nonce
    })
    result = result.payment_method_nonce.nonce
    if not result.is_success:
        error = True
        result = result.message
    return error, result


def create_braintree_payment(payment_method_nonce, customer_id, amount, billing=None, shipping=None):
    error = False
    data = {
        "amount": str(float(amount)),
        "order_id": "order id",
        "payment_method_nonce": payment_method_nonce,
        "customer_id": customer_id,
        "billing": billing if billing else {
            "first_name": "Paul",
            "last_name": "Smith",
            "company": "Braintree",
            "street_address": "1 E Main St",
            "extended_address": "Suite 403",
            "locality": "Chicago",
            "region": "IL",
            "postal_code": "60622",
            "country_code_alpha2": "US"
        },
        "shipping": shipping if shipping else {
            "first_name": "Jen",
            "last_name": "Smith",
            "company": "Braintree",
            "street_address": "1 E 1st St",
            "extended_address": "Suite 403",
            "locality": "Bartlett",
            "region": "IL",
            "postal_code": "60103",
            "country_code_alpha2": "US"
        },
        "options": {
            "submit_for_settlement": True
        },
    }
    result = gateway.transaction.sale(data)
    result = result.payment_method_nonce.nonce
    if not result.is_success:
        error = True
        result = result.message
    return error, result
