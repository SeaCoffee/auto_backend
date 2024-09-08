import os
import time
from celery import Celery
from celery.schedules import crontab
from django.db import OperationalError
from django.db import connection

# Устанавливаем настройки Django для использования в приложении.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

# Цикл для проверки доступности базы данных. Если соединение с базой данных не удается, ждем 3 секунды и повторяем попытку.
while True:
    try:
        # Проверяем соединение с базой данных.
        connection.ensure_connection()
        break  # Если подключение успешно, выходим из цикла.
    except OperationalError:
        # Если подключение не удалось, выводим сообщение и ждем 3 секунды перед новой попыткой.
        print("Database unavailable, waiting 3 seconds...")
        time.sleep(3)

# Когда подключение установлено, выводим сообщение.
print("Database connected. Starting Celery...")

# Создаем экземпляр приложения Celery с именем 'configs'.
app = Celery('configs')

# Загружаем настройки Celery из конфигурации Django. Все параметры Celery должны начинаться с префикса CELERY_.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Импортируем задачи из модуля `currency_service` для использования в Celery.
app.conf.imports = ('core.services.currency_service',)

# Автоматически обнаруживаем задачи из указанных модулей (в данном случае 'core.services').
app.autodiscover_tasks(['core.services'])

# Определяем расписание периодических задач (beat schedule) для Celery.
app.conf.beat_schedule = {
    # Задача для обновления курсов валют в полночь (каждый день в 00:01).
    'update-currency-rates-midnight': {
        'task': 'core.services.currency_service.update_currency_rates',  # Задача для выполнения.
        'schedule': crontab(hour=0, minute=1),  # Время выполнения.
    },
    # Задача для повторной попытки обновления курсов валют в полдень (каждый день в 12:00).
    'retry-update-currency-rates-noon': {
        'task': 'core.services.currency_service.update_currency_rates',  # Задача для выполнения.
        'schedule': crontab(hour=12, minute=0),  # Время выполнения.
    }
}

# Выводим сообщение о том, что задачи Celery зарегистрированы.
print("Celery tasks registered. Starting Celery...")


