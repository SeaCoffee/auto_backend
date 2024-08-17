from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import ProfileModel

UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Удалить пользователя и его профиль по email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email пользователя для удаления')

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        try:
            user = UserModel.objects.get(email=email)
            user_id = user.id  # Получаем ID пользователя для удаления профиля
            user.delete()  # Удаляем пользователя
            ProfileModel.objects.filter(user_id=user_id).delete()  # Удаляем профиль пользователя, если он остался
            self.stdout.write(self.style.SUCCESS(f"Пользователь и его профиль с email {email} были удалены."))
        except UserModel.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Пользователь с email {email} не найден."))
