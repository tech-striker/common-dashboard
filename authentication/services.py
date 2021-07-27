# project resources
from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
from utils.services.email_service import send_verification_email


def create_user(request, input_data):
    user = UserLoginInfo(**input_data)
    errors = user.clean()

    if errors:
        return errors
    else:
        user = UserLoginInfo.objects(email=input_data['email'].lower())
        if user:
            return generate_response(message='This email is already exist in our record, please login.')
        else:
            user = UserLoginInfo(**input_data)
        user.email = user.email.lower()
        user.save()
        send_verification_email(request, input_data, user)
        return generate_response(data=user.id, message='User Created', status=HTTP_201_CREATED)