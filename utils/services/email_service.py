import base64
from utils.common import account_activation_token
from multiprocessing import Process
from flask import render_template_string
from flask_mail import Message


def send_verification_email(request, input_data, user):
    from app import mail
    current_site = request.url_root
    mail_subject = 'Common Dashboard: Verify your account'
    domain = current_site
    uid = user.id
    token = account_activation_token.encode_token(user)
    msg = Message(
        mail_subject,
        sender='nkcse0007@gmail.com',
        recipients=[user.email]
    )
    msg.html = f"Please click on the link to confirm your registration, {domain}api/auth/verify-account/{uid}/{token}"
    mail.send(msg)
