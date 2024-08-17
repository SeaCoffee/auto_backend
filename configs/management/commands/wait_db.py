from django.core.management import BaseCommand
from django.db import OperationalError, connection
from django.db.backends.mysql.base import DatabaseWrapper
import time


connection: DatabaseWrapper=connection


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Waiting for db')
        db_con = False

        while not db_con:
            try:
                connection.ensure_connection()
                db_con = True
            except OperationalError:
                self.stdout.write('DB connection failed, wait 3 sec')
                time.sleep(3)

        self.stdout.write('DB connected')