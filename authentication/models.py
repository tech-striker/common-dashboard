from mongoengine import *
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


class Language(EmbeddedDocument):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = StringField(default='English')
    code = StringField(default='en')


class UserLoginInfo(AbstractBaseModel):
    parent = StringField(required=False)
    auth_type = StringField(choices=LOGIN_TYPE, required=True)
    role = StringField(choices=ROLE_TYPE, required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=6, regex=None)
    name = StringField(default='', required=False)
    phone = StringField(default='', required=False)
    intro = StringField(default='', required=False)
    profile_image = URLField(default='https://www.classifapp.com/wp-content/uploads/2017/09/avatar-placeholder.png',
                             required=False)
    social_id = StringField(default='', required=False)
    language = EmbeddedDocumentField(Language)
    is_active = BooleanField(default=True)
    is_deleted = BooleanField(default=False)
    is_verified = BooleanField(default=False)

    def generate_pw_hash(self):
        self.password = generate_password_hash(password=self.password).decode('utf-8')

    # Use documentation from BCrypt for password hashing
    generate_pw_hash.__doc__ = generate_password_hash.__doc__

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

    def save(self, *args, **kwargs):
        # Overwrite Document save method to generate password hash prior to saving
        if self._created:
            self.generate_pw_hash()
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
