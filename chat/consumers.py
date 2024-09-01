from channels.generic.websocket import AsyncWebsocketConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from channels.db import database_sync_to_async
from djangochannelsrestframework.decorators import action
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import ChatModel
from listings.models import ListingModel
import json

UserModel = get_user_model()


class ChatConsumer(GenericAsyncAPIConsumer):

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        self.room_name = None
        self.user_name = None
        self.listing_id = None

    async def connect(self):
        if not self.scope['user'] or self.scope['user'].is_anonymous:
            await self.close()
            return

        await self.accept()

        # Используем listing_id из URL
        self.listing_id = self.scope['url_route']['kwargs']['listing_id']
        self.room_name = f"listing_{self.listing_id}"
        self.user_name = await self.get_username()

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        # Отправка сообщения о подключении пользователя
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'sender',
                'message': f'{self.user_name} присоединился к чату для объявления {self.listing_id}'
            }
        )

        # Отправка предыдущих сообщений
        for message in await self.get_messages():
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'sender',
                    'message': message['body'],
                    'user': message['user']
                }
            )

    async def disconnect(self, close_code):
        if self.room_name:
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )

    async def sender(self, data):
        await self.send_json(data)

    async def receive_json(self, content):
        action = content.get('action')
        if action == 'send_message':
            if 'data' in content and 'request_id' in content:
                await self.send_message(data=content['data'], request_id=content.get('request_id'))
            else:
                await self.send_json({"error": "Недостаточно данных для отправки сообщения"})

    @action()
    async def send_message(self, **kwargs):
        try:
            data = kwargs.get('data')
            request_id = kwargs.get('request_id')
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'sender',
                    'message': data,
                    'user': self.user_name,
                    'id': request_id
                }
            )
            await self.save_message_to_db(data, self.scope['user'])

        except Exception as e:
            print(f"Ошибка при отправке сообщения: {str(e)}")
            await self.send_json({"error": str(e)})

    @database_sync_to_async
    def get_username(self):
        if self.scope['user'].is_authenticated:
            return self.scope['user'].username
        return "Anonymous"

    @database_sync_to_async
    def save_message_to_db(self, body, user):
        # Сохранение сообщения с привязкой к конкретному объявлению
        ChatModel.objects.create(body=body, user=user, listing_id=self.listing_id)

    @database_sync_to_async
    def get_messages(self):
        # Получение сообщений для конкретного объявления
        return [{'body': item.body, 'user': item.user.username} for item in ChatModel.objects.filter(listing_id=self.listing_id).order_by('id')]
