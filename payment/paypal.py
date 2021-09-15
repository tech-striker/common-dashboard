# from django.http.response import JsonResponse
import json

import requests

# Create your views here

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest,OrdersGetRequest,OrdersCaptureRequest,OrdersAuthorizeRequest
from paypalcheckoutsdk.payments import AuthorizationsGetRequest,AuthorizationsCaptureRequest,CapturesGetRequest,CapturesRefundRequest,RefundsGetRequest


client_id = (
    "AQiFCVhmweyjrGg9-91swA0fp61lRhCH6Ht5gt0fFR_e9RGVKdb2uXEAK6GYHChFCnUzERzVE0H7hNrE"
)
client_secret = (
    "EO2JQOOHBHLeKAGnCgRe8TlghZzILwJ9pw9dmgTIGvN9uidaFn55rfXTDakYc98gI3eG-qaa_clDcRz9"
)
environment = SandboxEnvironment(client_id, client_secret)
client = PayPalHttpClient(environment)

from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalhttp import HttpError

# Here, OrdersCreateRequest() creates a POST request to /v2/checkout/orders
def create_capture_order(currency_code, amount):
    order_instance = OrdersCreateRequest()
    order_instance.prefer("return=representation")
    order_instance.request_body(
        {
        "intent": "CAPTURE",
        "purchase_units": [
          {
            "description": "Sporting Goods",
            "amount": {
              "currency_code": currency_code,
              "value": str(amount),

            },
       
          }
        ],
        "application_context": {
        "return_url": "http://127.0.0.1:5000/api/payment/paypal/create-capture-order"
    
  }
      }

    )
    try:
        # Call API with your client and get a response for your call
        order_create = client.execute(order_instance)
        response = order_create.result.dict()
    except Exception as exp:
        print(exp)
        response = json.loads(exp.message)

    return response

def get_order(order_id):
    order_instance = OrdersGetRequest(order_id)
    try:  
        order_details = client.execute(order_instance)
        response= order_details.result.dict()
    except Exception as e:
        print(e)
        response = json.loads(e.message)
    return response

def capture_order(order_id):
    order_instance = OrdersCaptureRequest(order_id)
    try:
        order_captured = client.execute(order_instance)
        response = order_captured.result.dict()
    except Exception as e:
        print(e)
        response = json.loads(e.message)
    return response

def get_captured_order(capture_id):
    order_instance = CapturesGetRequest(capture_id)
    try:  
        order_details = client.execute(order_instance)
        response= order_details.result.dict()
    except Exception as e:
        print(e)
        response = json.loads(e.message)
    return response

def create_authorize_order(currency_code, amount):
    order_instance = OrdersCreateRequest()
    order_instance.prefer("return=representation")
    order_instance.request_body(
        {
        "intent": "AUTHORIZE",
        "purchase_units": [
          {
            "description": "Sporting Goods",
            "amount": {
              "currency_code": currency_code,
              "value": str(amount),

            },
       
          }
        ],
        "application_context": {
        "return_url": "http://127.0.0.1:8000/myapp/index"
    
  }
      }

    )
    try:
        # Call API with your client and get a response for your call
        order_create = client.execute(order_instance)
        response = order_create.result.dict()
    except Exception as e:
        print(e)
        response = json.loads(e.message)

    return response

def authorize_order(order_id):
    order_instance = OrdersAuthorizeRequest(order_id)
    order_instance.prefer("return=representation")
    order_instance.request_body({})
    try:
        order_authorized = client.execute(order_instance)
        response = order_authorized.result.dict()
    except  Exception as e:
        print(e)
        response = json.loads(e.message)
    return response

def get_authorized_order(authorization_id):
    order_instance = AuthorizationsGetRequest(authorization_id)
    try:  
        order_details = client.execute(order_instance)
        response= order_details.result.dict()
    except Exception as e:
        print(e)
        response = json.loads(e.message)
    return response
        
def capture_auth(authorization_id):
        authorization_instance = AuthorizationsCaptureRequest(authorization_id)
        authorization_instance.request_body({})
        try:
            captured_order = client.execute(authorization_instance)
            response = captured_order.result.dict()
        except Exception as e:
            print(e)
            response = json.loads(e.message)

        return response

def capture_refund(capture_id):
        refund_instance = CapturesRefundRequest(capture_id)
        refund_instance.request_body({})
        try:
            refund_order = client.execute(refund_instance)
            response = refund_order.result.dict()
        except Exception as e:
            print(e)
            response = json.loads(e.message)

        return response

def get_refund_details(refund_id):
    refund_instance = RefundsGetRequest(refund_id)
    try:  
        refund_details = client.execute(refund_instance)
        response= refund_details.result.dict()
    except Exception as e:
        print(e)
        response = json.loads(e.message)
    return response