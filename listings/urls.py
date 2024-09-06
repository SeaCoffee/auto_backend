from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import ListingCreateView, PremiumStatsView, ListingUpdateView, \
    ListingDeleteView, ListingListView, ListingAddPhotoAPIView,\
    RegionsAPIView, UserListingsView, ListingRetrieveView, ListingRetrieveDetailView, BrandRequestView



urlpatterns = [
    path('create/', ListingCreateView.as_view(), name='listing-create'),
    path('regions/', RegionsAPIView.as_view(), name='regions_enum'),
    path('user/', UserListingsView.as_view(), name='user-listings'),
    path('update/<int:pk>/', ListingUpdateView.as_view(), name='listing_update'),
    path('photo/<int:listing_id>/', ListingAddPhotoAPIView.as_view(), name='add__listing_photo'),
    path('list/', ListingListView.as_view(), name='listing_list'),
    path('details/<int:pk>/', ListingRetrieveView.as_view(), name='listing-detail'),
    path('cardetails/<int:pk>/', ListingRetrieveDetailView.as_view(), name='listing-detail'),
    path('delete/<int:pk>/', ListingDeleteView.as_view(), name='listing-delete'),
    path('premium/<int:listing_id>/stats/', PremiumStatsView.as_view(), name='premium_stats'),
    path('brands/request/', BrandRequestView.as_view(), name='brand-request'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

