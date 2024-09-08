from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import ProfileModel

UserModel = get_user_model()

class Command(BaseCommand):
    """
    Команда для удаления пользователя и его профиля по email. Используется в терминале.
    """

    help = 'Удалить пользователя и его профиль по email'

    def add_arguments(self, parser):
        """
        Добавляем аргумент для команды - email пользователя, которого нужно удалить.
        """
        parser.add_argument('email', type=str, help='Email пользователя для удаления')

    def handle(self, *args, **kwargs):
        """
        Основной метод, выполняющий удаление пользователя по email. Также удаляется профиль пользователя.
        """
        email = kwargs['email']
        try:
            # Ищем пользователя по email
            user = UserModel.objects.get(email=email)
            user_id = user.id  # Получаем ID пользователя для удаления его профиля
            user.delete()  # Удаляем пользователя
            ProfileModel.objects.filter(user_id=user_id).delete()  # Удаляем связанный профиль
            self.stdout.write(self.style.SUCCESS(f"Пользователь и его профиль с email {email} были удалены."))
        except UserModel.DoesNotExist:
            # Если пользователь не найден, выводим сообщение об ошибке
            self.stdout.write(self.style.ERROR(f"Пользователь с email {email} не найден."))

