from django.contrib.auth import get_user_model
from .email_service import EmailService
import random
from configs.celery import app


class ManagerNotificationService:
    """
    Сервис для отправки уведомлений менеджерам. Содержит методы для отправки различных уведомлений, таких как
    оповещения о попытках редактирования или ненормативной лексике в объявлениях.
    """

    @staticmethod
    def send_notification(brand_name, model_name, username):
        """
        Отправляет уведомление менеджерам о попытках редактирования объявления.
        Если в базе данных есть менеджеры (пользователи с role_id = 3), выбирается случайный менеджер,
        которому будет отправлено уведомление по электронной почте.
        :param brand_name: Название бренда автомобиля
        :param model_name: Название модели автомобиля
        :param username: Имя пользователя, совершившего действие
        """
        UserModel = get_user_model()
        managers = UserModel.objects.filter(role_id=3)  # Находим всех менеджеров (role_id=3)

        if not managers.exists():
            print("No managers found with role_id = 3.")  # Сообщение, если менеджеров не найдено
            return

        # Выбираем случайного менеджера из списка найденных
        manager = random.choice(managers)

        # Контекст для шаблона письма
        context = {
            'brand_name': brand_name,
            'model_name': model_name,
            'username': username
        }
        subject = 'Review Listing Edit Attempts'  # Тема письма
        template_name = 'manager_notification_email.html'  # Шаблон для письма

        # Отправляем письмо через асинхронную задачу Celery
        EmailService.send_email.delay(manager.email, template_name, context, subject)

    @staticmethod
    def send_profanity_notification(description, username, manager):
        """
        Отправляет уведомление менеджеру, если в описании объявления обнаружена ненормативная лексика.
        :param description: Описание объявления с ненормативной лексикой
        :param username: Имя пользователя, создавшего или редактировавшего объявление
        :param manager: Менеджер, который должен получить уведомление
        """
        # Контекст для шаблона письма
        context = {
            'description': description,
            'username': username
        }
        subject = 'Profanity Alert: Review Listing'  # Тема письма
        template_name = 'profanity_notification_email.html'  # Шаблон для письма

        # Отправляем письмо через асинхронную задачу Celery
        EmailService.send_email.delay(manager.email, template_name, context, subject)
