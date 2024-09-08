from django.urls import path
from chat.routing import websocket_urlpatterns as chat_routing
from channels.routing import URLRouter


# Определение маршрутов для WebSocket-соединений.
websocket_urlpatterns = [
    # Путь для подключения к WebSocket API для чата. Используется URLRouter для обработки запросов чата.
    path('api/chat/', URLRouter(chat_routing))
]