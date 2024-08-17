from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

import os
from core.services.jwt_service import JWTService, ActivateToken, RecoveryToken
from core.dataclases.user_dataclass import UserDataClass

class EmailService:
    @staticmethod
    def send_email(to: str, template_name: str, context: dict, subject=''):
        template = get_template(template_name)
        html_content = template.render(context)
        msg = EmailMultiAlternatives(subject, body="", from_email=os.environ.get('EMAIL_HOST_USER'), to=[to])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

    @classmethod
    def register(cls, user: UserDataClass):
        token = JWTService.create_token(user, ActivateToken)
        url = f"http://localhost:3000/activate/{token}"
        cls.send_email(
            user.email,
            'register.html',
            {'name': user.profile.name, 'url': url},
            'Register'
        )

    @classmethod
    def recovery_password(cls, user):
        token = JWTService.create_token(user, RecoveryToken)
        url = f"http://localhost:3000/recovery/{token}"
        cls.send_email(
            user.email,
            'recovery.html',
            {'url': url},
            'Recovery Password'
        )

    @classmethod
    def account_deletion(cls, user: UserDataClass):
        cls.send_email(
            user.email,
            'delete_account.html',
            {'name': user.username},
            'Your Account Has Been Deleted'
        )
