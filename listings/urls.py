from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import ListingCreateView, PremiumStatsView, ListingUpdateView, \
    ListingDeleteView, ListingListView, ListingAddPhotoAPIView,\
    RegionsAPIView, UserListingsView, ListingRetrieveView, ListingRetrieveDetailView, \
    BrandRequestView



urlpatterns = [
    path('create/', ListingCreateView.as_view(), name='listing-create'),  # Создание нового объявления
    path('regions/', RegionsAPIView.as_view(), name='regions_enum'),  # Получение списка регионов
    path('user/', UserListingsView.as_view(), name='user-listings'),  # Список объявлений текущего пользователя
    path('update/<int:pk>/', ListingUpdateView.as_view(), name='listing_update'),  # Обновление объявления
    path('photo/<int:listing_id>/', ListingAddPhotoAPIView.as_view(), name='add__listing_photo'),  # Добавление фото к объявлению
    path('list/', ListingListView.as_view(), name='listing_list'),  # Список всех объявлений
    path('details/<int:pk>/', ListingRetrieveView.as_view(), name='listing-detail'),  # Детали объявления
    path('cardetails/<int:pk>/', ListingRetrieveDetailView.as_view(), name='listing-detail'),  # Детализированные данные объявления
    path('delete/<int:pk>/', ListingDeleteView.as_view(), name='listing-delete'),  # Удаление объявления
    path('premium/<int:listing_id>/stats/', PremiumStatsView.as_view(), name='premium_stats'),  # Статистика по премиум объявлениям
    path('brands/request/', BrandRequestView.as_view(), name='brand-request'),  # Запрос на добавление нового бренда
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

