from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserActivateAPIView, UserRecoverAPIView,\
    ResetPasswordAPIView, CustomTokenObtainPairView, RoleListAPIView, SoketView


urlpatterns = [
    path('', CustomTokenObtainPairView.as_view(), name='user_auth_login'),  # Аутентификация пользователя (получение токенов).
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление токена доступа.
    path('activate/<str:token>/', UserActivateAPIView.as_view(), name='activate-account'),  # Активация аккаунта.
    path('recovery/', UserRecoverAPIView.as_view(), name='recovery-password'),  # Запрос на восстановление пароля.
    path('recovery/<str:token>', ResetPasswordAPIView.as_view(), name='recovery-password'),  # Сброс пароля.
    path('roles/', RoleListAPIView.as_view(), name='role-list'),  # Список всех ролей.
    path('soket/', SoketView.as_view(), name='soket'),  # Получение сокет-токена.
]
