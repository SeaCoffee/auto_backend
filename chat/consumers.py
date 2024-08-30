from channels.generic.websocket import AsyncWebsocketConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from channels.db import database_sync_to_async
from djangochannelsrestframework.decorators import action

from chat.models import ChatModel

class ChatConsumer(GenericAsyncAPIConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.user_name = None

    async def connect(self):
        if not self.scope['user'] or self.scope['user'].is_anonymous:
            await self.close()
            return

        await self.accept()

        self.room_name = self.scope['url_route']['kwargs']['room']
        self.user_name = await self.get_username()

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )


        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'sender',
                'message': f'{self.user_name} joined the room {self.room_name}'
            }
        )

        for message in await self.get_messages():
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'sender',
                    'message':message['body'],
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
        ChatModel.objects.create(body=body, user=user)

    @database_sync_to_async
    def get_messages(self):
        return[{'body':item.body, 'user':item.user.username} for item in ChatModel.objects.order_by('id')]
