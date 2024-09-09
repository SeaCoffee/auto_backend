from django.db import models
from django.contrib.auth import get_user_model


from core.models import BaseModel
from listings.models import ListingModel


UserModel = get_user_model()
"""
Получаем модель пользователя, которая используется в приложении.
Это кастомная модель пользователя.
"""

class ChatModel(BaseModel):
    """
    Модель для хранения сообщений чата. Наследуется от BaseModel, что добавляет поля, такие как дата создания
    и изменения.
    """

    class Meta:
        # Определяем имя таблицы в базе данных как 'chat'.
        db_table = 'chat'

    # Поле для текста сообщения. Максимальная длина сообщения - 255 символов.
    body = models.CharField(max_length=255)

    # Связь с пользователем, который отправил сообщение. При удалении пользователя сообщение тоже будет удалено (CASCADE).
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    # Связь с объявлением, к которому относится сообщение. Если объявление удалено, сообщения тоже будут удалены (CASCADE).
    # Поле допускает null и пустые значения, если сообщение не привязано к конкретному объявлению.
    listing = models.ForeignKey(ListingModel, on_delete=models.CASCADE, null=True, blank=True, related_name='chats')

    # Поле для идентификатора чата. Оно может использоваться для группировки сообщений по чатам.
    chat_id = models.CharField(max_length=255)

