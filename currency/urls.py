from django.urls import path
from .views import CurrencyAPIView

urlpatterns = [
    path('list/', CurrencyAPIView.as_view(), name='api-currencies'),
]
