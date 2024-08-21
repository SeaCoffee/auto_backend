from django.urls import path

from .views import UserCreateAPIView, UpgradeAccountAPIView, ProfileDetailView,\
    CreateManagerView, UserAddAvatarAPIView, UserDeleteSelfView, AddToBlacklistView, CurrentUsereDetailsView

urlpatterns = [
    path('', UserCreateAPIView.as_view(), name='user-create'),
    path('upgrade_account/', UpgradeAccountAPIView.as_view({'put': 'update'}), name='upgrade-account'),
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('create_manager/', CreateManagerView.as_view(), name='create_manager'),
    path('avatars/', UserAddAvatarAPIView.as_view(), name='add_avatar'),
    path('delete-account/', UserDeleteSelfView.as_view(), name='delete-account'),
    path('blacklist/manage/', AddToBlacklistView.as_view(), name='manage-blacklist'),
    path('user/', CurrentUsereDetailsView.as_view(), name='current-user'),
]