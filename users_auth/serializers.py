from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserRoleModel
UserModel = get_user_model()

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('password',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)


        token['account_type'] = user.account_type
        if user.role:
            token['role'] = user.role.name

        return token


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoleModel
        fields = ['id', 'name']