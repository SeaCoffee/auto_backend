from celery import shared_task
import requests
from datetime import datetime
from django.db import transaction
from currency.models import CurrencyModel

PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"

@shared_task(bind=True, max_retries=3, default_retry_delay=3600)
def update_currency_rates(self):
    try:
        response = requests.get(PRIVATBANK_API_URL)
        response.raise_for_status()

        rates = response.json()
        target_currencies = {'USD', 'EUR', 'UAH'}

        with transaction.atomic():
            for rate in rates:
                currency_code = rate['ccy']
                if currency_code in target_currencies and float(rate['sale']) > 0:
                    CurrencyModel.objects.update_or_create(
                        currency_code=currency_code,
                        defaults={'rate': float(rate['sale']), 'updated_at': datetime.now()}
                    )
    except Exception as e:
        self.retry(exc=e)

