from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('api/users/', include('users.urls')),
    path('api/auth/', include('users_auth.urls')),
    path('api/cars/', include('cars.urls')),
    path('api/listings/', include('listings.urls')),
    path('api/currencies/', include('currency.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

