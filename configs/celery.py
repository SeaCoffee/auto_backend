import os
import time
from celery import Celery
from celery.schedules import crontab
from django.db import OperationalError
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

while True:
    try:
        connection.ensure_connection()
        break
    except OperationalError:
        print("Database unavailable, waiting 3 seconds...")
        time.sleep(3)

print("Database connected. Starting Celery...")


app = Celery('configs')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.imports = ('core.services.currency_service',)


app.autodiscover_tasks(['core.services'])


app.conf.beat_schedule = {
    'update-currency-rates-midnight': {
        'task': 'core.services.currency_service.update_currency_rates',
        'schedule': crontab(hour=0, minute=1),
    },
    'retry-update-currency-rates-noon': {
        'task': 'core.services.currency_service.update_currency_rates',
        'schedule': crontab(hour=12, minute=0),
    }
}

print("Celery tasks registered. Starting Celery...")


