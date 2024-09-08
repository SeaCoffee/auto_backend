from django.urls import path
from .consumers import ChatConsumer


# Определение маршрутов для WebSocket-соединений.
websocket_urlpatterns = [
    # Путь для подключения к WebSocket по ID объявления. Используется ChatConsumer для обработки соединений.
    path('<int:listing_id>/', ChatConsumer.as_asgi()),
]