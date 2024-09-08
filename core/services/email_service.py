from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import os

from configs.celery import app
from core.services.jwt_service import JWTService, ActivateToken, RecoveryToken
from core.dataclases.user_dataclass import UserDataClass

class EmailService:
    """
    Сервис для отправки писем. Содержит статические и классовые методы для отправки email по разным событиям.
    """

    @staticmethod
    @app.task
    def send_email(to: str, template_name: str, context: dict, subject=''):
        """
        Статический метод для отправки email с использованием Celery задачи.
        """
        # Загружаем HTML-шаблон письма
        template = get_template(template_name)
        html_content = template.render(context)  # Рендерим шаблон с переданными данными
        msg = EmailMultiAlternatives(subject, body="", from_email=os.environ.get('EMAIL_HOST_USER'), to=[to])
        msg.attach_alternative(html_content, 'text/html')  # Добавляем HTML-контент в письмо
        msg.send()  # Отправляем письмо

    @classmethod
    def register(cls, user: UserDataClass):
        """
        Метод для отправки email после регистрации пользователя.
        Генерирует токен для активации аккаунта и отправляет письмо с ссылкой на активацию.
        """
        token = JWTService.create_token(user, ActivateToken)
        url = f"http://localhost/activate/{token}"  # Генерируем URL для активации аккаунта
        # Отправляем письмо с подтверждением регистрации через задачу Celery
        cls.send_email.delay(
            user.email,
            'register.html',
            {'name': user.profile.name, 'url': url},
            'Register'
        )

    @classmethod
    def recovery_password(cls, user):
        """
        Метод для отправки email для восстановления пароля.
        Генерирует токен для восстановления и отправляет письмо с ссылкой на страницу восстановления.
        """
        token = JWTService.create_token(user, RecoveryToken)
        url = f"http://localhost/recovery/{token}"  # Генерируем URL для восстановления пароля
        # Отправляем письмо для восстановления пароля через задачу Celery
        cls.send_email.delay(
            user.email,
            'recovery.html',
            {'url': url},
            'Recovery Password'
        )

    @classmethod
    def account_deletion(cls, user: UserDataClass):
        """
        Метод для отправки email при удалении аккаунта пользователя.
        Отправляет письмо с уведомлением о том, что аккаунт был удален.
        """
        # Отправляем письмо об удалении аккаунта через задачу Celery
        cls.send_email.delay(
            user.email,
            'delete_account.html',
            {'name': user.username},
            'Your Account Has Been Deleted'
        )