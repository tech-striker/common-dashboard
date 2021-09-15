from werkzeug.routing import ValidationError

from app import db
from utils.common import generate_response
from utils.constants import *
from utils.db.base_model import AbstractBaseModel
from flask_bcrypt import generate_password_hash, check_password_hash
import phonenumbers
import re
import uuid


def validate_phone(value):
    try:
        phonenumbers.parse(value)
        return True
    except ValidationError:
        return False


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(regex, email):
        return True

    else:
        return False


class Language(db.EmbeddedDocument):
    title = db.StringField(default='English')
    code = db.StringField(default='en')


class UserLocation(db.EmbeddedDocument):
    latlong = db.GeoPointField(required=False)
    address = db.StringField(default='', required=False)
    city = db.StringField(default='', required=False)
    country = db.StringField(default='', required=False)
    pin = db.StringField(default='', required=False)


class UserLoginInfo(AbstractBaseModel):
    parent = db.StringField(required=False)
    auth_type = db.StringField(choices=LOGIN_TYPE, required=True)
    role = db.StringField(choices=ROLE_TYPE, required=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6, regex=None)
    name = db.StringField(default='', required=False)
    phone = db.StringField(default='', required=False)
    phone_code = db.StringField(default='', required=False)
    intro = db.StringField(default='', required=False)
    profile_image = db.URLField(default='https://www.classifapp.com/wp-content/uploads/2017/09/avatar-placeholder.png',
                                required=False)
    social_id = db.StringField(default='', required=False)
    language = db.EmbeddedDocumentField(Language)
    location = db.EmbeddedDocumentField(UserLocation, default=dict)
    is_active = db.BooleanField(default=True)
    is_deleted = db.BooleanField(default=False)
    is_verified = db.BooleanField(default=False)

    def generate_pw_hash(self):
        self.password = generate_password_hash(password=self.password).decode('utf-8')
        return self.password

    def check_pw_hash(self, password: str) -> bool:
        return check_password_hash(pw_hash=self.password, password=password)

    # Use documentation from BCrypt for password hashing
    check_pw_hash.__doc__ = check_password_hash.__doc__

    def clean(self):
        if not self.email or not type(self.email) == str or not validate_email(self.email):
            return generate_response(message='Email is missing or invalid.')
        if not self.password or not type(self.password) == str or not len(self.password) > 6:
            return generate_response(message='Password is missing or invalid. password should be minimum 6 characters.')
        if not self.role or not type(self.role) == str or self.role not in ROLE_TYPE:
            return generate_response(message='Password is missing or invalid.')
        if not self.auth_type or not type(self.auth_type) == str or self.auth_type not in LOGIN_TYPE:
            return generate_response(message='Auth type is missing or invalid.')
        return None

    def create_user(self, *args, **kwargs):
        user = UserLoginInfo(**kwargs)
        user.email = kwargs['email']
        user.password = self.generate_pw_hash()
        # user.save()
        super(UserLoginInfo, self).save(*args, **kwargs)

    meta = {
        'auto_create_index': True,
        'index_background': True,
        'indexes': [
            {
                'name': 'email',
                'fields': ('email',),
                'unique': True
            },
            {
                'name': 'created_at',
                'fields': ('created_at',)
            }
        ]
    }

    def to_json(self, *args, **kwargs):
        return {
            "id": str(self.pk),
            "role": self.role,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "intro": self.intro,
            "profile_image": self.profile_image,
            "language": self.language,
            "location": self.location,
            "is_active": self.is_active,
            "auth_type": self.auth_type
        }
