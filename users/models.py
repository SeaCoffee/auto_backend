from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core import validators

from users_auth.models import UserRoleModel
from core.models import BaseModel
from .manager import UserManager
from core.services.upload_photos import upload_avatar
from core.enums.regex_enum import RegexEnum


# Варианты типов аккаунтов для пользователя
ACCOUNT_TYPES = [('basic', 'Basic'), ('premium', 'Premium')]


class UserModel(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Модель пользователя, расширяющая стандартные возможности Django пользователей.
    Включает дополнительные поля, такие как роль и тип аккаунта.
    """
    email = models.EmailField(unique=True)  # Поле email должно быть уникальным для каждого пользователя.
    username = models.CharField(max_length=55, unique=True)  # Уникальное имя пользователя с максимальной длиной 55 символов.
    password = models.CharField(
        max_length=128,
        validators=[validators.RegexValidator(*RegexEnum.PASSWORD.value)]  # Валидация пароля с использованием регулярного выражения.
    )
    is_active = models.BooleanField(default=False)  # Поле для статуса активации пользователя.
    is_staff = models.BooleanField(default=False)  # Определяет, является ли пользователь сотрудником.
    role = models.ForeignKey(
        UserRoleModel,
        on_delete=models.CASCADE,
        related_name='users',
        default=1  # Роль пользователя, по умолчанию '1'.
    )
    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPES,
        default='basic'  # Поле для хранения типа аккаунта (basic или premium).
    )
    is_upgrade_to_premium = models.BooleanField(default=False)  # Флаг, указывающий, подал ли пользователь запрос на обновление до премиум аккаунта.

    # Поле для входа пользователя
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Обязательные поля при создании пользователя.

    objects = UserManager()  # Кастомный менеджер для пользователей.

    class Meta:
        db_table = 'custom_auth_user'  # Имя таблицы в базе данных.


class ProfileModel(BaseModel):
    """
    Модель профиля пользователя, содержащая дополнительную информацию о пользователе, такую как имя, фамилия, возраст и аватар.
    """
    name = models.CharField(
        max_length=55,
        validators=[validators.RegexValidator(*RegexEnum.NAME.value)]  # Валидация имени пользователя.
    )
    surname = models.CharField(
        max_length=55,
        validators=[validators.RegexValidator(*RegexEnum.NAME.value)]  # Валидация фамилии пользователя.
    )
    age = models.IntegerField(
        validators=[validators.MinValueValidator(16), validators.MaxValueValidator(100)],  # Ограничения на возраст.
        null=True,
        blank=True
    )
    city = models.CharField(max_length=100)  # Город проживания пользователя.
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        related_name='profile'  # Связь один-к-одному с пользователем.
    )
    avatar = models.ImageField(
        upload_to=upload_avatar,  # Путь для загрузки аватара.
        blank=True,
        null=True,
        validators=(validators.FileExtensionValidator(['jpeg', 'jpg', 'png']),)  # Валидация типа загружаемого файла.
    )

    class Meta:
        db_table = 'profile'  # Имя таблицы в базе данных.


class BlacklistModel(BaseModel):
    """
    Модель черного списка, в которой хранится информация о заблокированных пользователях, причина и время блокировки.
    """
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        related_name='blacklist_entry'  # Связь с пользователем, который добавлен в черный список.
    )
    added_by = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_blacklist_entries'  # Пользователь, который добавил другого в черный список.
    )
    reason = models.TextField(null=True, blank=True)  # Причина добавления в черный список (необязательно).
    added_at = models.DateTimeField(auto_now_add=True)  # Дата и время добавления в черный список.

    class Meta:
        db_table = 'blacklist'  # Имя таблицы в базе данных.
