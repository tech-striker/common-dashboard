# from flask_jwt_extended import create_access_token, create_refresh_token

# project resources
from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
import datetime
import random
from utils.jwt.jwt_security import JwtAuth
import os
from payment.services import stripe_create_payment_customer

expiry = datetime.timedelta(days=5)


def login_user(request, input_data):
    try:
        user = UserLoginInfo.objects.get(email=input_data.get('email').lower())
    except:
        return generate_response(message='No record found with this email, please signup first.')
    auth_success = user.check_pw_hash(input_data.get('password'))
    if not auth_success:
        return generate_response(message='Email or password you provided is invalid. please check it once',
                                 status=HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return generate_response(message='User is blocked by admin, Please contact admin.',
                                 status=HTTP_401_UNAUTHORIZED)
    if user.is_deleted:
        return generate_response(message='User has deleted their account previously, please contact admin.',
                                 status=HTTP_401_UNAUTHORIZED)
    if not user.is_verified:
        return generate_response(message='User is not verified his account, please check your email.',
                                 status=HTTP_401_UNAUTHORIZED)
    else:
        # access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
        # refresh_token = create_refresh_token(identity=str(user.id))

        access_token, refresh_token = get_refresh_access_token(request, user)
        return generate_response(data={'access_token': access_token,
                                       'refresh_token': refresh_token,
                                       'logged_in_as': f"{user.email}",
                                       'meta': user.to_json()
                                       }, status=HTTP_200_OK)


def social_login(request, input_data):
    new_user = False
    try:
        user = UserLoginInfo.objects.get(email=input_data['email'].lower())
    except:
        user = UserLoginInfo(**input_data)
        new_user = True
        # provider random default password
        user.password = str(random.randint(10000000, 99999999))
    errors = user.clean()
    if errors:
        return errors
    if 'social_id' not in input_data or not input_data['social_id']:
        return generate_response(message='Social id is missing or invalid.')

    user.email = input_data['email'].lower()
    user.role = input_data['role']
    user.auth_type = input_data['auth_type']
    user.social_id = input_data['social_id']
    user.is_active = True
    user.is_verified = True
    # if input_data['role'] == B2B_USER:
    #     user.parent = self.input_data['parent']
    user.save()
    if new_user:
        stripe_create_payment_customer(user)

    access_token, refresh_token = get_refresh_access_token(request, user)
    return generate_response(data={'access_token': access_token,
                                   'refresh_token': refresh_token,
                                   'logged_in_as': f"{user.email}",
                                   'meta': user
                                   }, status=HTTP_200_OK)


def update_user(input_data, user):
    if 'name' in input_data and input_data['name']:
        user.name = input_data['name']
    if 'phone' in input_data and input_data['phone']:
        if 'phone_code' not in input_data or not input_data['phone_code']:
            return generate_response(message='Phone code is required')
        user.phone_code = input_data['phone_code']
        user.phone = input_data['phone']
    if 'profile_image' in input_data and input_data['profile_image']:
        user.profile_image = input_data['profile_image']
    if 'intro' in input_data and input_data['intro']:
        user.intro = input_data['intro']
    if 'is_active' in input_data:
        user.is_active = True
    user.save()
    return generate_response(data=user.to_json(), message='User updated', status=HTTP_200_OK)


def get_refresh_access_token(request, user):
    Jwt = JwtAuth(os.environ.get('VERIFY_TOKEN'))
    response = {
        'id': str(user.id),
        'name': user.name,
        'phone': user.phone,
        'email': user.email,
        'role': user.role,
        'auth_type': user.auth_type,
    }
    return Jwt.encode(response, request, user)
