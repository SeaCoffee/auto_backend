from django.urls import path

from .views import UserCreateAPIView, UpgradeAccountAPIView, ProfileDetailView,\
    CreateManagerView, UserAddAvatarAPIView, UserDeleteSelfView, AddToBlacklistView, CurrentUsereDetailsView


urlpatterns = [
    path('', UserCreateAPIView.as_view(), name='user-create'),  # Создание пользователя.
    path('upgrade_account/', UpgradeAccountAPIView.as_view({'put': 'update'}), name='upgrade-account'),  # Обновление аккаунта до премиум.
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),  # Получение профиля.
    path('create_manager/', CreateManagerView.as_view(), name='create_manager'),  # Создание менеджера.
    path('avatars/', UserAddAvatarAPIView.as_view(), name='add_avatar'),  # Добавление аватара.
    path('delete-account/', UserDeleteSelfView.as_view(), name='delete-account'),  # Удаление учетной записи.
    path('blacklist/manage/', AddToBlacklistView.as_view(), name='manage-blacklist'),  # Управление черным списком.
    path('user/', CurrentUsereDetailsView.as_view(), name='current-user'),  # Получение данных текущего пользователя.
]