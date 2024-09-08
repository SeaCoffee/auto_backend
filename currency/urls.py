from django.urls import path
from .views import CurrencyAPIView

urlpatterns = [
    # Маршрут для API списка валют. Связываем URL с представлением `CurrencyAPIView`.
    path('list/', CurrencyAPIView.as_view(), name='api-currencies'),
]
