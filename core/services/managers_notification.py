from django.contrib.auth import get_user_model
from .email_service import EmailService
import random
from configs.celery import app


class ManagerNotificationService:
    @staticmethod
    def send_notification(brand_name, model_name, username):
        UserModel = get_user_model()
        managers = UserModel.objects.filter(role_id=3)
        if not managers.exists():
            print("No managers found with role_id = 3.")
            return

        manager = random.choice(managers)
        context = {
            'brand_name': brand_name,
            'model_name': model_name,
            'username': username
        }
        subject = 'Review Listing Edit Attempts'
        template_name = 'manager_notification_email.html'
        EmailService.send_email.delay(manager.email, template_name, context, subject)

    @staticmethod
    def send_profanity_notification(description, username, manager):
        context = {
            'description': description,
            'username': username
        }
        subject = 'Profanity Alert: Review Listing'
        template_name = 'profanity_notification_email.html'
        EmailService.send_email.delay(manager.email, template_name, context, subject)
