from django.core.management.base import BaseCommand
from users.models import ProfileModel

class Command(BaseCommand):
    """
    Команда для удаления профиля по его ID. Используется в терминале для удаления конкретного профиля.
    """

    # Описание команды, которое будет отображаться при вызове `python manage.py help <command>`.
    help = 'Удалить профиль по id профиля'

    def add_arguments(self, parser):
        """
        Метод для добавления аргументов, принимаемых командой. В данном случае требуется ID профиля.
        """
        parser.add_argument('profile_id', type=int, help='ID профиля, который нужно удалить')

    def handle(self, *args, **kwargs):
        """
        Основной метод, который выполняется при запуске команды.
        Получаем ID профиля и пытаемся найти и удалить профиль по этому ID.
        """
        profile_id = kwargs['profile_id']
        try:
            # Ищем профиль по ID
            profile = ProfileModel.objects.get(id=profile_id)
            profile.delete()  # Удаляем профиль
            self.stdout.write(self.style.SUCCESS(f"Профиль с ID {profile_id} был удален."))
        except ProfileModel.DoesNotExist:
            # Если профиль не найден, выводим сообщение об ошибке
            self.stdout.write(self.style.ERROR(f"Профиль с ID {profile_id} не найден."))
