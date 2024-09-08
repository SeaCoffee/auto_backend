from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from channels.db import database_sync_to_async
from djangochannelsrestframework.decorators import action

from django.contrib.auth import get_user_model

from chat.models import ChatModel


UserModel = get_user_model()
"""
Получаем модель пользователя, которая используется в приложении.
Это кастомная модель пользователя.
"""

class ChatConsumer(GenericAsyncAPIConsumer):
    """
    Асинхронный WebSocket Consumer для обработки сообщений чата, связанных с объявлениями (listing).
    Наследуется от GenericAsyncAPIConsumer, который упрощает работу с WebSocket-сообщениями.
    """

    def init(self, *args, **kwargs):
        """
        Инициализация переменных, которые будут использоваться для обработки сообщений и управления комнатой.
        """
        super().init(*args, **kwargs)
        self.room_name = None  # Название комнаты чата, привязанной к объявлению.
        self.user_name = None  # Имя пользователя, присоединившегося к чату.
        self.listing_id = None  # ID объявления, с которым связан чат.

    async def connect(self):
        """
        Обрабатывает новое подключение к WebSocket. Если пользователь не авторизован, закрываем соединение.
        Если авторизован, принимаем соединение и добавляем пользователя в группу (комнату) чата.
        """
        # Если пользователь анонимный или неавторизованный, закрываем соединение.
        if not self.scope['user'] or self.scope['user'].is_anonymous:
            await self.close()
            return

        # Принимаем WebSocket соединение.
        await self.accept()

        # Получаем ID объявления из URL.
        self.listing_id = self.scope['url_route']['kwargs']['listing_id']
        # Формируем название комнаты чата на основе объявления.
        self.room_name = f"listing_{self.listing_id}"
        # Получаем имя пользователя.
        self.user_name = await self.get_username()

        # Добавляем пользователя в группу (комнату) чата.
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        # Отправляем сообщение в чат, что пользователь присоединился.
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'sender',  # Тип события, который будет вызван.
                'message': f'{self.user_name} присоединился к чату для объявления {self.listing_id}'
            }
        )

        # Отправляем все прошлые сообщения в чат для нового пользователя.
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
        """
        Обрабатывает отключение пользователя от WebSocket. Убирает пользователя из группы (комнаты).
        """
        if self.room_name:
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )

    async def sender(self, data):
        """
        Отправляет данные в WebSocket. Этот метод вызывается, когда необходимо отправить сообщение в чат.
        """
        await self.send_json(data)

    async def receive_json(self, content):
        """
        Обрабатывает получение сообщения в формате JSON от клиента.
        Если action == 'send_message', то сообщение отправляется в чат.
        """
        action = content.get('action')
        if action == 'send_message':
            if 'data' in content and 'request_id' in content:
                await self.send_message(data=content['data'], request_id=content.get('request_id'))
            else:
                await self.send_json({"error": "Недостаточно данных для отправки сообщения"})

    @action()
    async def send_message(self, **kwargs):
        """
        Отправляет сообщение в группу чата и сохраняет его в базе данных.
        """
        try:
            # Получаем данные сообщения и идентификатор запроса.
            data = kwargs.get('data')
            request_id = kwargs.get('request_id')

            # Отправляем сообщение в группу чата.
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'sender',
                    'message': data,
                    'user': self.user_name,
                    'id': request_id
                }
            )

            # Сохраняем сообщение в базе данных.
            await self.save_message_to_db(data, self.scope['user'])

        except Exception as e:
            # Логируем и отправляем ошибку при неудачной отправке сообщения.
            print(f"Ошибка при отправке сообщения: {str(e)}")
            await self.send_json({"error": str(e)})

    @database_sync_to_async
    def get_username(self):
        """
        Получаем имя пользователя из текущего запроса. Если пользователь не аутентифицирован, возвращаем 'Anonymous'.
        """
        if self.scope['user'].is_authenticated:
            return self.scope['user'].username
        return "Anonymous"

    @database_sync_to_async
    def save_message_to_db(self, body, user):
        """
        Сохраняем сообщение в базе данных. Сообщение привязывается к пользователю и объявлению.
        """
        ChatModel.objects.create(body=body, user=user, listing_id=self.listing_id)

    @database_sync_to_async
    def get_messages(self):
        """
        Получаем все сообщения, связанные с текущим объявлением, сортируя их по id (по времени создания).
        """
        return [{'body': item.body, 'user': item.user.username} for item in ChatModel.objects.filter(listing_id=self.listing_id).order_by('id')]
