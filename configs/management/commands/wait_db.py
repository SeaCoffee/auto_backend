from django.core.management import BaseCommand
from django.db import OperationalError, connection
from django.db.backends.mysql.base import DatabaseWrapper
import time

connection: DatabaseWrapper = connection
"""
Объект `connection` представляет подключение к базе данных. Используется для взаимодействия с базой.
"""


class Command(BaseCommand):
    """
    Команда для ожидания подключения к базе данных. Полезно для сценариев, где требуется убедиться в наличии соединения
    с базой данных перед выполнением действий.
    """

    def handle(self, *args, **kwargs):
        """
        Основной метод команды. Проверяет наличие подключения к базе данных и повторяет попытку подключения при ошибке.
        """
        self.stdout.write('Waiting for db')
        db_con = False

        # Цикл для ожидания успешного подключения к базе данных
        while not db_con:
            try:
                # Проверяем соединение с базой данных
                connection.ensure_connection()
                db_con = True  # Если подключение успешно, устанавливаем флаг
            except OperationalError:
                # Если подключение не удалось, ждем 3 секунды и повторяем попытку
                self.stdout.write('DB connection failed, wait 3 sec')
                time.sleep(3)

        # Когда соединение установлено, выводим сообщение об успешном подключении
        self.stdout.write('DB connected')