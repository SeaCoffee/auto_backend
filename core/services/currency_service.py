from celery import shared_task
import requests
from datetime import datetime
from django.db import transaction
from currency.models import CurrencyModel

PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
"""
URL для получения актуальных курсов валют от PrivatBank. 
Запрос возвращает данные в формате JSON для использования в обновлении валютных курсов.
"""


@shared_task(bind=True, max_retries=3, default_retry_delay=3600)
def update_currency_rates(self):
    """
    Асинхронная задача для обновления курсов валют.
    Запрашивает данные с API PrivatBank, фильтрует по целевым валютам (USD, EUR, UAH) и обновляет курс в базе данных.
    Задача может быть повторена до 3 раз с задержкой 1 час в случае ошибки.
    """
    try:
        # Выполняем запрос к API PrivatBank
        response = requests.get(PRIVATBANK_API_URL)
        response.raise_for_status()  # Проверяем статус ответа

        # Получаем данные в формате JSON
        rates = response.json()
        target_currencies = {'USD', 'EUR', 'UAH'}  # Целевые валюты

        # Используем транзакцию для атомарности обновлений
        with transaction.atomic():
            for rate in rates:
                currency_code = rate['ccy']  # Получаем код валюты
                if currency_code in target_currencies and float(rate['sale']) > 0:
                    # Обновляем или создаем запись в базе данных для каждой валюты
                    CurrencyModel.objects.update_or_create(
                        currency_code=currency_code,
                        defaults={'rate': float(rate['sale']), 'updated_at': datetime.now()}
                    )
    except Exception as e:
        # В случае ошибки задача будет повторена через час, максимум 3 раза
        self.retry(exc=e)