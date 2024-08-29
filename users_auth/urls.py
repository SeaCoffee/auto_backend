from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserActivateAPIView, UserRecoverAPIView,\
    ResetPasswordAPIView, CustomTokenObtainPairView, RoleListAPIView, SoketView


urlpatterns = [
    path('', CustomTokenObtainPairView.as_view(), name='user_auth_login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('activate/<str:token>/', UserActivateAPIView.as_view(), name='activate-account'),
    path('recovery/', UserRecoverAPIView.as_view(), name='recovery-password'),
    path('recovery/<str:token>', ResetPasswordAPIView.as_view(), name='recovery-password'),
    path('roles/', RoleListAPIView.as_view(), name='role-list'),
    path('soket/', SoketView.as_view(), name='soket'),
]