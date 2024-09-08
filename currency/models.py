from django.db import models
from core.models import BaseModel

class CurrencyModel(BaseModel):
    """
    Модель для хранения валют и их курсов.
    Наследуется от `BaseModel`, что добавляет поля `created_at` и `updated_at` для отслеживания времени создания и обновления записи.
    """

    currency_code = models.CharField(max_length=3)  # Код валюты (например, USD, EUR). Максимальная длина - 3 символа.
    rate = models.FloatField()  # Курс валюты по отношению к базовой валюте.

    class Meta:
        # Уникальность комбинации полей `currency_code` и `updated_at` для предотвращения дублирования данных за один день.
        unique_together = ('currency_code', 'updated_at')
        db_table = 'currency'  # Имя таблицы в базе данных.