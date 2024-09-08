from rest_framework.generics import GenericAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status

from core.services.jwt_service import JWTService, ActivateToken, RecoveryToken, SoketToken
from users.serializers import UserSerializer
from .serializers import EmailSerializer, PasswordSerializer, \
    CustomTokenObtainPairSerializer, UserRoleSerializer
from core.services.email_service import EmailService
from .models import UserRoleModel

UserModel = get_user_model()


class UserActivateAPIView(GenericAPIView):
    permission_classes = [AllowAny]  # Доступ открыт для всех.

    def get(self, request, *args, **kwargs):
        """
        Активация аккаунта через GET запрос.
        """
        token = kwargs['token']
        try:
            user = JWTService.validate_token(token, ActivateToken)
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully! Please log in.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, *args, **kwargs):
        """
        Активация аккаунта через POST запрос.
        """
        token = kwargs['token']
        try:
            user = JWTService.validate_token(token, ActivateToken)
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Представление для запроса восстановления пароля
class UserRecoverAPIView(GenericAPIView):
    permission_classes = [AllowAny]  # Доступ открыт для всех.
    serializer_class = EmailSerializer

    def post(self, *args, **kwargs):
        """
        Отправка запроса на восстановление пароля.
        """
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            user = get_object_or_404(UserModel, **serializer.validated_data)
        except Http404:
            raise
        EmailService.recovery_password(user)
        return Response({'details': 'check email'}, status=status.HTTP_200_OK)


# Представление для сброса пароля
class ResetPasswordAPIView(GenericAPIView):
    permission_classes = [AllowAny]  # Доступ открыт для всех.
    serializer_class = PasswordSerializer

    def post(self, *args, **kwargs):
        """
        Сброс пароля через POST запрос.
        """
        data = self.request.data
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = kwargs['token']
        try:
            user = JWTService.validate_token(token, RecoveryToken)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Установка нового пароля
        new_password = serializer.validated_data['password']
        user.set_password(new_password)
        user.is_active = True
        user.save()

        return Response({'message': 'Password has been changed'}, status=status.HTTP_200_OK)


# Кастомное представление для получения пары токенов
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Представление для получения пары токенов (доступ и обновление).
    """
    serializer_class = CustomTokenObtainPairSerializer  # Используем кастомный сериализатор.


# Представление для списка ролей
class RoleListAPIView(ListAPIView):
    """
    Представление для получения списка ролей.
    """
    queryset = UserRoleModel.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [AllowAny]  # Доступ открыт для всех.


# Представление для получения сокет-токена
class SoketView(GenericAPIView):
    """
    Представление для получения сокет-токена для аутентифицированных пользователей.
    """
    permission_classes = [IsAuthenticated]  # Доступ только для аутентифицированных пользователей.

    def get(self, *args, **kwargs):
        """
        Возвращает сокет-токен для текущего пользователя.
        """
        token = JWTService.create_token(self.request.user, SoketToken)
        return Response({'token': str(token)}, status.HTTP_200_OK)