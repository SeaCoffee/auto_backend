from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserRoleModel

UserModel = get_user_model()

# Сериализатор для email
class EmailSerializer(serializers.Serializer):
    """
    Сериализатор для обработки email.
    """
    email = serializers.EmailField()  # Поле для email.


# Сериализатор для пароля
class PasswordSerializer(serializers.ModelSerializer):
    """
    Сериализатор для изменения пароля.
    """
    class Meta:
        model = UserModel
        fields = ('password',)  # Поле пароля.


# Кастомный сериализатор для токенов (JWT)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения пары токенов (добавляет роль и тип аккаунта в токен).
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавляем тип аккаунта и роль в токен
        token['account_type'] = user.account_type
        if user.role:
            token['role'] = user.role.name

        return token


# Сериализатор роли пользователя
class UserRoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели UserRoleModel.
    """
    class Meta:
        model = UserRoleModel
        fields = ['id', 'name']  # Поля для сериализации.
