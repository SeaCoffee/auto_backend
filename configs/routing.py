from django.urls import path
from chat.routing import websocket_urlpatterns as chat_routing
from channels.routing import URLRouter

websocket_urlpatterns = [
path('api/chat/', URLRouter(chat_routing))
]