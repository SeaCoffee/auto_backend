from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from .email_service import EmailService
import os
import random


class ManagerNotificationService:
    @staticmethod
    def send_notification(brand_name, model_name, username):
        UserModel = get_user_model()
        managers = UserModel.objects.filter(role_id=3)
        if not managers.exists():
            print("No managers found with role_id = 3.")
            return

        # Выбор случайного менеджера
        manager = random.choice(managers)
        context = {
            'brand_name': brand_name,
            'model_name': model_name,
            'username': username
        }
        subject = 'Review Listing Edit Attempts'
        template_name = 'manager_notification_email.html'
        ManagerNotificationService.__send_email(manager.email, template_name, context, subject)

    @staticmethod
    def send_profanity_notification(description, username, manager):
        context = {
            'description': description,
            'username': username
        }
        subject = 'Profanity Alert: Review Listing'
        template_name = 'profanity_notification_email.html'
        ManagerNotificationService.__send_email(manager.email, template_name, context, subject)

    @staticmethod
    def __send_email(to: str, template_name: str, context: dict, subject=''):
        template = get_template(template_name)
        html_content = template.render(context)
        msg = EmailMultiAlternatives(subject, body="", from_email=os.environ.get('EMAIL_HOST_USER'), to=[to])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()