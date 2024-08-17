from django.core.management.base import BaseCommand
from users.models import ProfileModel

class Command(BaseCommand):
    help = 'Удалить профиль по id профиля'

    def add_arguments(self, parser):
        parser.add_argument('profile_id', type=int, help='ID профиля, который нужно удалить')

    def handle(self, *args, **kwargs):
        profile_id = kwargs['profile_id']
        try:
            profile = ProfileModel.objects.get(id=profile_id)
            profile.delete()
            self.stdout.write(self.style.SUCCESS(f"Профиль с ID {profile_id} был удален."))
        except ProfileModel.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Профиль с ID {profile_id} не найден."))
