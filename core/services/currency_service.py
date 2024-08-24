import requests
from configs.celery import app
from datetime import datetime
from currency.models import CurrencyModel
from django.db import transaction
from celery import shared_task

class CurrencyService:
    PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"

    @staticmethod
    @shared_task(bind=True, max_retries=3, default_retry_delay=3600)  # Ретрай каждый час в случае ошибки
    def update_currency_rates(self):
        try:
            response = requests.get(CurrencyService.PRIVATBANK_API_URL)
            response.raise_for_status()  # Выбросить исключение для ошибок HTTP

            rates = response.json()
            # Курсы, которые нас интересуют
            target_currencies = {'USD', 'EUR', 'UAH'}

            with transaction.atomic():
                for rate in rates:
                    currency_code = rate['ccy']
                    if currency_code in target_currencies:
                        CurrencyModel.objects.update_or_create(
                            currency_code=currency_code,
                            defaults={'rate': float(rate['sale']), 'updated_at': datetime.now()}
                        )
            print("Currency rates updated successfully.")

        except requests.exceptions.RequestException as e:
            print(f"Failed to update currency rates: {e}")
            self.retry(exc=e)

