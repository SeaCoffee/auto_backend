from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from users_auth.models import UserRoleModel
from core.services.email_service import EmailService
from .models import UserModel, ProfileModel, BlacklistModel
from django.apps import apps

class UserRoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели UserRoleModel, которая определяет роль пользователя.
    """
    class Meta:
        model = UserRoleModel
        fields = ('id', 'name', 'created_at', 'updated_at')  # Поля, которые будут сериализованы.


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProfileModel, которая хранит информацию о профиле пользователя.
    """
    role = serializers.CharField(source='user.role.name', read_only=True)  # Поле для отображения роли пользователя.
    account_type = serializers.CharField(source='user.account_type', read_only=True)  # Тип аккаунта пользователя.
    avatar = serializers.ImageField(read_only=True)  # Поле для отображения аватара пользователя.

    class Meta:
        model = ProfileModel
        fields = ('id', 'name', 'surname', 'age', 'city', 'role', 'account_type', 'avatar')  # Поля, которые будут сериализованы.


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения подробной информации о пользователе, включая его профиль.
    """
    profile = ProfileSerializer(read_only=True)  # Поле профиля пользователя.

    class Meta:
        model = UserModel
        fields = ('username', 'role', 'account_type', 'profile')  # Поля, которые будут сериализованы.


class UserSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для модели пользователя, который используется для создания и обновления пользователей.
    """
    profile = ProfileSerializer()  # Вложенный сериализатор профиля.
    role = serializers.PrimaryKeyRelatedField(queryset=UserRoleModel.objects.all())  # Поле для выбора роли пользователя.

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'username', 'is_active', 'is_staff', 'is_superuser',
                  'last_login', 'created_at', 'updated_at', 'profile', 'role', 'account_type')  # Поля для сериализации.
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'last_login',
                            'created_at', 'updated_at')  # Поля, которые нельзя изменять напрямую.
        extra_kwargs = {
            'password': {'write_only': True}  # Поле пароля только для записи.
        }

    @atomic
    def create(self, validated_data):
        """
        Создание нового пользователя с ролью и профилем.
        """
        profile_data = validated_data.pop('profile', None)
        role = validated_data.pop('role')

        user = UserModel.objects.create_user(role=role, profile_data=profile_data, **validated_data)  # Создание пользователя через кастомный менеджер.
        print(f"Sending registration email to {user.email}")
        EmailService.register(user)  # Отправка email при регистрации.

        ProfileModel = apps.get_model('users', 'ProfileModel')
        if profile_data and not ProfileModel.objects.filter(user=user).exists():
            ProfileModel.objects.create(user=user, **profile_data)  # Создание профиля, если его нет.

        return user


class UpgradeAccountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления типа аккаунта до 'premium'.
    """
    class Meta:
        model = get_user_model()
        fields = ['account_type']  # Поле для обновления типа аккаунта.

    def validate_account_type(self, value):
        """
        Валидация типа аккаунта — можно только обновить до 'premium'.
        """
        if value != 'premium':
            raise serializers.ValidationError("Only upgrade to 'premium' is allowed.")
        return value

    def update(self, instance, validated_data):
        """
        Обновление типа аккаунта до 'premium' и установка флага 'is_upgrade_to_premium'.
        """
        instance.account_type = validated_data['account_type']
        instance.is_upgrade_to_premium = True
        instance.save()
        return instance


class ManagerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания менеджеров. Только суперпользователи или администраторы могут создавать менеджеров.
    """
    profile = ProfileSerializer(required=False)  # Профиль не обязателен при создании.
    role = serializers.PrimaryKeyRelatedField(queryset=UserRoleModel.objects.all(), default=3)  # Роль по умолчанию — менеджер.

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'username', 'is_active', 'is_staff', 'is_superuser',
                  'last_login', 'created_at', 'updated_at', 'profile', 'role', 'account_type')  # Поля для сериализации.
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'created_at', 'updated_at', 'role')  # Нельзя менять роль после создания.
        extra_kwargs = {
            'password': {'write_only': True},  # Поле пароля только для записи.
            'is_staff': {'default': True},  # По умолчанию `is_staff=True`.
            'is_active': {'default': True}  # По умолчанию `is_active=True`.
        }

    @atomic
    def create(self, validated_data):
        """
        Создание менеджера с проверкой прав текущего пользователя.
        """
        UserModel = get_user_model()
        creator_user = self.context['request'].user

        if not (creator_user.is_superuser or (creator_user.is_staff and creator_user.role.name == 'admin')):
            raise serializers.ValidationError("Only superusers or admins can create managers")  # Проверка прав на создание менеджера.

        profile_data = validated_data.pop('profile', None)
        validated_data['is_staff'] = True  # Менеджеры всегда сотрудники.
        validated_data['is_active'] = True  # Менеджеры всегда активны.
        user = UserModel.objects.create_user(**validated_data)  # Создаем пользователя-менеджера.

        ProfileModel = apps.get_model('users', 'ProfileModel')
        if profile_data and not ProfileModel.objects.filter(user=user).exists():
            ProfileModel.objects.create(user=user, **profile_data)  # Создаем профиль для менеджера.

        return user


class ProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModel
        fields = ('avatar',)

    def validate_avatar(self, avatar):
        max_size = 100 * 1024  # 100 KB
        if avatar.size > max_size:
            raise serializers.ValidationError('The avatar size exceeds the maximum limit of 100 KB.')
        return avatar

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class BlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistModel
        fields = ['user', 'reason', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


