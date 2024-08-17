from django.contrib.auth.models import BaseUserManager as Manager
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from core.services.email_service import EmailService
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

from users_auth.models import UserRoleModel



class UserManager(Manager):

    @atomic
    def create_user(self, email, username, password=None, role=None, account_type='basic', profile_data=None,
                    **extra_fields):
        if not email:
            raise ValueError('Email required')
        if not username:
            raise ValueError('Username required')
        if not password:
            raise ValueError('Password required')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)

        if role:
            if isinstance(role, UserRoleModel):
                user.role = role
            else:
                user.role_id = role
        else:
            user.role_id = 1  # Устанавливаем роль по умолчанию, если роль не предоставлена

        user.account_type = account_type
        user.save()

        # Создаем профиль только для обычных пользователей
        if not user.is_superuser:
            ProfileModel = apps.get_model('users', 'ProfileModel')
            if profile_data:
                ProfileModel.objects.create(user=user, **profile_data)
            else:
                ProfileModel.objects.create(user=user)

        return user

    @atomic
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must be True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be True')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Active must be True')

        role_id = 4
        user = self.create_user(email, username, password, role=role_id, **extra_fields)
        return user

    @atomic
    def create_manager(self, creator_user, email, username, password=None, **extra_fields):
        if not (creator_user.is_superuser or (creator_user.is_staff and creator_user.role.name == 'admin')):
            raise PermissionError("Only superusers or admins can create managers")

        extra_fields.setdefault('is_staff', True)
        extra_fields['is_active'] = True

        if self.model is None:
            raise ValueError("Model is not initialized.")

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must be True for a manager')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Active must be True for a manager')

        role_id = 3
        user = self.create_user(email, username, password, role=role_id, account_type='premium', **extra_fields)
        return user


    @atomic
    def delete_own_user(self, user):
        if not self.model.objects.filter(id=user.id).exists():
            raise ValueError("User with given ID does not exist")

        #EmailService.account_deletion(user)
        user.delete()
        return "Your account has been deleted successfully."
