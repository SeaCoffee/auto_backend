from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('users/', include('users.urls')),
    path('auth/', include('users_auth.urls')),
    path('cars/', include('cars.urls')),
    path('listings/', include('listings.urls')),
    path('currencies/', include('currency.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)