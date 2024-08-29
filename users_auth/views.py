from rest_framework.generics import GenericAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
import logging
logger = logging.getLogger(__name__)

class UserActivateAPIView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        logger.debug(f"Activating user with token: {token}")
        try:
            user = JWTService.validate_token(token, ActivateToken)
            user.is_active = True
            user.save()
            logger.debug(f"User {user.username} activated successfully.")
            # Перенаправление на страницу входа или другую страницу
            return Response({'message': 'Account activated successfully! Please log in.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, *args, **kwargs):
        token = kwargs['token']
        logger.debug(f"Activating user with token: {token}")
        try:
            user = JWTService.validate_token(token, ActivateToken)
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserRecoverAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        print(f"Received data: {data}")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        print(f"Validated data: {serializer.validated_data}")  # Логгирование валидированных данных
        try:
            user = get_object_or_404(UserModel, **serializer.validated_data)
            print(f"User found: {user.email}")  # Подтверждение, что пользователь найден
        except Http404:
            print("User not found")  # Логгирование случая, если пользователь не найден
            raise
        EmailService.recovery_password(user)
        return Response({'details': 'check email'}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print("Serializer validation failed: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = kwargs['token']
        try:
            user = JWTService.validate_token(token, RecoveryToken)
            print(f"User before password change: {user.password}")
        except Exception as e:
            print("Token validation error: ", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Выводим новый пароль перед установкой (в реальной системе это небезопасно!)
        new_password = serializer.validated_data['password']
        print(f"New password to be set: {new_password}")

        # Установка нового пароля и сохранение пользователя
        user.set_password(new_password)
        user.is_active = True
        user.save()

        # Проверяем, что пароль изменился
        print(f"User after password change: {user.password}")

        return Response({'message': 'Password has been changed'}, status=status.HTTP_200_OK)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RoleListAPIView(ListAPIView):
    queryset = UserRoleModel.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [AllowAny]


class SoketView(GenericAPIView):
    permission_classes = (IsAuthenticated)

    def get(self, *args, **kwargs):
        token = JWTService.create_token(self.request.user, SoketToken)
        return Response({'token':str(token)}, status.HTTP_200_OK)