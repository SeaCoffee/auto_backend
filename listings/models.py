from django.db import models
from core.models import BaseModel
from cars.models import CarModel
from django.core import validators
from decimal import Decimal

from .manager import ListingManager
from currency.models import CurrencyModel
from core.enums.country_region_enum import Region
from core.services.upload_photos import upload_photo_listing


class ListingModel(BaseModel):
    """
    Модель для хранения информации об объявлениях. Содержит данные о машине, продавце, цене, валюте, регионе и другом.
    """

    car = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='listings')  # Связь с моделью автомобиля.
    seller = models.ForeignKey('users.UserModel', on_delete=models.CASCADE, related_name='listings')  # Продавец, разместивший объявление.
    title = models.CharField(max_length=255)  # Заголовок объявления.
    description = models.TextField()  # Описание объявления.
    listing_photo = models.ImageField(
        upload_to='upload_photo_listing',  # Путь для загрузки изображений.
        blank=True,
        null=True,
        validators=[validators.FileExtensionValidator(['jpeg', 'jpg', 'png'])]  # Валидация расширений файлов.
    )
    active = models.BooleanField(default=False)  # Статус объявления (активно/неактивно).
    views_day = models.IntegerField(default=0)  # Количество просмотров за день.
    views_week = models.IntegerField(default=0)  # Количество просмотров за неделю.
    views_month = models.IntegerField(default=0)  # Количество просмотров за месяц.
    edit_attempts = models.IntegerField(default=0)  # Количество попыток редактирования объявления.
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена товара.
    currency = models.ForeignKey(CurrencyModel, on_delete=models.SET_NULL, null=True, related_name='listings')  # Валюта, в которой указана цена.
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)  # Цена в USD.
    price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)  # Цена в EUR.
    price_uah = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)  # Цена в UAH.
    region = models.CharField(max_length=50, choices=Region.choices(), default=Region.KYIV.value)  # Регион, где размещено объявление.
    year = models.IntegerField()  # Год выпуска автомобиля.
    engine = models.CharField(max_length=255)  # Двигатель автомобиля.
    initial_currency_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, editable=False)  # Начальный курс валюты.

    objects = ListingManager()  # Использование кастомного менеджера объявлений.

    def save(self, *args, **kwargs):
        """
        Переопределение метода `save` для пересчета цены в других валютах на основе текущих курсов валют.
        """
        # Получаем актуальные курсы валют.
        rates = CurrencyModel.objects.all().values('currency_code', 'rate')
        rates_dict = {rate['currency_code']: Decimal(rate['rate']) for rate in rates}

        # Базовый курс валюты для расчета.
        base_rate = rates_dict.get(self.currency.currency_code, Decimal('1'))

        # Пересчет цены в доллары, евро и гривны.
        if base_rate != Decimal('0'):
            self.price_usd = (self.price / base_rate) * rates_dict.get('USD', Decimal('1'))
            self.price_eur = (self.price / base_rate) * rates_dict.get('EUR', Decimal('1'))
            self.price_uah = (self.price / base_rate) * rates_dict.get('UAH', Decimal('1'))
        else:
            # Если курс валюты нулевой, устанавливаем нулевые значения для цены в других валютах.
            self.price_usd = Decimal('0')
            self.price_eur = Decimal('0')
            self.price_uah = Decimal('0')

        # Сохраняем объект.
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'listings'  # Имя таблицы в базе данных.

    def increment_views(self):
        """
        Увеличивает количество просмотров для объявления на день, неделю и месяц.
        """
        self.views_day += 1
        self.views_week += 1
        self.views_month += 1
        # Обновляем только поля количества просмотров.
        self.save(update_fields=['views_day', 'views_week', 'views_month'])


