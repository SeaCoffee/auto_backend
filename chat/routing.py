from django.urls import path
from .consumers import ChatConsumer


websocket_urlpatterns = [
    path('<int:listing_id>/', ChatConsumer.as_asgi()),
]
