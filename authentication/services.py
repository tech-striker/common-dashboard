# project resources
from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
from utils.services.email_service import send_verification_email
from payment.services import stripe_create_payment_customer


def create_user(request, input_data):
    user = UserLoginInfo.objects(email=input_data['email'].lower())
    if user:
        return generate_response(message='This email is already exist in our record, please login.')
    user = UserLoginInfo(**input_data)
    errors = user.clean()
    if errors:
        return errors
    user.email = user.email.lower()
    user.create_user(**input_data)
    stripe_create_payment_customer(user)
    send_verification_email(request, input_data, user)
    return generate_response(data=user.to_json(), message='User Created', status=HTTP_201_CREATED)
