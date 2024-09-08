from django.contrib.auth.models import BaseUserManager as Manager
from django.db.transaction import atomic
from django.apps import apps

from core.services.email_service import EmailService
from users_auth.models import UserRoleModel

from django.contrib.auth import get_user_model

class UserManager(Manager):
    """
    Кастомный менеджер для управления пользователями, включая создание обычных пользователей, суперпользователей и менеджеров.
    """

    @atomic
    def create_user(self, email, username, password=None, role=None, account_type='basic', profile_data=None,
                    **extra_fields):
        """
        Создает нового пользователя с заданными параметрами. Также создает профиль для обычных пользователей.
        :param email: Email пользователя
        :param username: Имя пользователя
        :param password: Пароль пользователя
        :param role: Роль пользователя (по умолчанию роль 1)
        :param account_type: Тип аккаунта (по умолчанию 'basic')
        :param profile_data: Дополнительные данные для профиля
        :param extra_fields: Дополнительные поля для модели пользователя
        :return: Созданный пользователь
        """
        if not email:
            raise ValueError('Email required')  # Проверка на обязательное наличие email.
        if not username:
            raise ValueError('Username required')  # Проверка на обязательное наличие имени пользователя.
        if not password:
            raise ValueError('Password required')  # Проверка на обязательное наличие пароля.

        email = self.normalize_email(email)  # Нормализация email.
        user = self.model(email=email, username=username, **extra_fields)  # Создание пользователя без сохранения в базе данных.
        user.set_password(password)  # Хеширование пароля.

        if role:
            # Если передана роль, устанавливаем ее.
            if isinstance(role, UserRoleModel):
                user.role = role
            else:
                user.role_id = role  # Присваиваем ID роли.
        else:
            user.role_id = 1  # Устанавливаем роль по умолчанию, если роль не предоставлена.

        user.account_type = account_type  # Устанавливаем тип аккаунта.
        user.save()  # Сохраняем пользователя в базе данных.

        # Создаем профиль для обычных пользователей (кроме суперпользователей).
        if not user.is_superuser:
            ProfileModel = apps.get_model('users', 'ProfileModel')  # Динамическое получение модели профиля.
            if profile_data:
                ProfileModel.objects.create(user=user, **profile_data)  # Создаем профиль с дополнительными данными.
            else:
                ProfileModel.objects.create(user=user)  # Создаем профиль по умолчанию.

        return user

    @atomic
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Создает суперпользователя. Устанавливает соответствующие флаги для администратора.
        :param email: Email пользователя
        :param username: Имя пользователя
        :param password: Пароль пользователя
        :param extra_fields: Дополнительные поля для модели пользователя
        :return: Созданный суперпользователь
        """
        extra_fields.setdefault('is_staff', True)  # Устанавливаем флаг `is_staff` по умолчанию.
        extra_fields.setdefault('is_superuser', True)  # Устанавливаем флаг `is_superuser` по умолчанию.
        extra_fields.setdefault('is_active', True)  # Устанавливаем флаг `is_active` по умолчанию.

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must be True')  # Проверка, что пользователь является сотрудником.
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be True')  # Проверка, что пользователь является суперпользователем.
        if extra_fields.get('is_active') is not True:
            raise ValueError('Active must be True')  # Проверка, что пользователь активен.

        role_id = 4  # Устанавливаем роль суперпользователя.
        user = self.create_user(email, username, password, role=role_id, **extra_fields)  # Создаем пользователя с ролью суперпользователя.
        return user

    @atomic
    def create_manager(self, creator_user, email, username, password=None, **extra_fields):
        """
        Создает менеджера. Только суперпользователи или администраторы могут создавать менеджеров.
        :param creator_user: Пользователь, создающий менеджера (должен быть суперпользователем или администратором).
        :param email: Email менеджера
        :param username: Имя пользователя менеджера
        :param password: Пароль менеджера
        :param extra_fields: Дополнительные поля для модели пользователя
        :return: Созданный менеджер
        """
        if not (creator_user.is_superuser or (creator_user.is_staff and creator_user.role.name == 'admin')):
            raise PermissionError("Only superusers or admins can create managers")  # Проверка прав на создание менеджера.

        extra_fields.setdefault('is_staff', True)  # Устанавливаем флаг `is_staff` по умолчанию.
        extra_fields['is_active'] = True  # Менеджер должен быть активен.

        if self.model is None:
            raise ValueError("Model is not initialized.")  # Проверка инициализации модели.

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must be True for a manager')  # Проверка, что менеджер является сотрудником.
        if extra_fields.get('is_active') is not True:
            raise ValueError('Active must be True for a manager')  # Проверка, что менеджер активен.

        role_id = 3  # Роль менеджера.
        user = self.create_user(email, username, password, role=role_id, account_type='premium', **extra_fields)  # Создаем менеджера с ролью и типом аккаунта.
        return user

    @atomic
    def delete_own_user(self, user):
        """
        Удаляет учетную запись пользователя.
        :param user: Пользователь, который удаляется
        :return: Сообщение об успешном удалении
        """
        if not self.model.objects.filter(id=user.id).exists():
            raise ValueError("User with given ID does not exist")  # Проверка существования пользователя.

        # EmailService.account_deletion(user)  # Закомментирован вызов сервиса отправки уведомления о удалении.
        user.delete()  # Удаление пользователя из базы данных.
        return "Your account has been deleted successfully."  # Возвращаем сообщение об успешном удалении.
