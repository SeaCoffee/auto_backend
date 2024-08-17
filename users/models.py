from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core import validators

from users_auth.models import UserRoleModel
from core.models import BaseModel
from .manager import UserManager
from core.services.upload_photos import upload_avatar
from core.enums.regex_enum import RegexEnum


ACCOUNT_TYPES = [('basic', 'Basic'), ('premium', 'Premium')]


class UserModel(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=55, unique=True)
    password = models.CharField(max_length=128, validators=[validators.RegexValidator(*RegexEnum.PASSWORD.value)])
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.ForeignKey(UserRoleModel, on_delete=models.CASCADE, related_name='users', default=1)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='basic')
    is_upgrade_to_premium = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        db_table = 'custom_auth_user'


class ProfileModel(BaseModel):
    name = models.CharField(max_length=55, validators=[validators.RegexValidator(*RegexEnum.NAME.value)])
    surname = models.CharField(max_length=55, validators=[validators.RegexValidator(*RegexEnum.NAME.value)])
    age = models.IntegerField(validators=[validators.MinValueValidator(16), validators.MaxValueValidator(100)], null=True, blank=True)
    city = models.CharField(max_length=100)
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to=upload_avatar,
        blank=True,
        null=True,
        validators=(validators.FileExtensionValidator(['jpeg', 'jpg', 'png']),)
    )

    class Meta:
        db_table = 'profile'


class BlacklistModel(BaseModel):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='blacklist_entry')
    added_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, related_name='added_blacklist_entries')
    reason = models.TextField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

