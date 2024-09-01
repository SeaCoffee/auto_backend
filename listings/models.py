from django.db import models
from core.models import BaseModel
from cars.models import CarModel
from core.services.upload_photos import upload_photo_listing
from django.core import validators
from decimal import Decimal
from .manager import ListingManager

from currency.models import CurrencyModel
from core.enums.country_region_enum import Region

class ListingModel(BaseModel):
    car = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='listings')
    seller = models.ForeignKey('users.UserModel', on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    listing_photo = models.ImageField(upload_to='upload_photo_listing', blank=True, null=True, validators=[validators.FileExtensionValidator(['jpeg', 'jpg', 'png'])])
    active = models.BooleanField(default=False)
    views_day = models.IntegerField(default=0)
    views_week = models.IntegerField(default=0)
    views_month = models.IntegerField(default=0)
    edit_attempts = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(CurrencyModel, on_delete=models.SET_NULL, null=True, related_name='listings')
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)
    price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)
    price_uah = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)
    region = models.CharField( max_length=50, choices=Region.choices(), default=Region.KYIV.value)
    year = models.IntegerField()
    engine = models.CharField(max_length=255)

    objects = ListingManager()
    def save(self, *args, **kwargs):
        rates = CurrencyModel.objects.all().values('currency_code', 'rate')
        rates_dict = {rate['currency_code']: Decimal(rate['rate']) for rate in rates}

        # Получение базового курса для текущей валюты объявления
        base_rate = rates_dict.get(self.currency.currency_code,
                                   Decimal('1'))  # Установка значения по умолчанию на 1, если валюта не найдена

        # Проверка, что базовый курс не равен нулю, чтобы избежать деления на ноль
        if base_rate != Decimal('0'):
            # Пересчет цен с учетом курса валют
            self.price_usd = (self.price / base_rate) * rates_dict.get('USD', Decimal('1'))  # USD курс по умолчанию
            self.price_eur = (self.price / base_rate) * rates_dict.get('EUR', Decimal('1'))  # EUR курс по умолчанию
            self.price_uah = (self.price / base_rate) * rates_dict.get('UAH', Decimal('1'))  # UAH курс по умолчанию
        else:
            # Если базовый курс равен нулю, установим цены как нулевые значения
            self.price_usd = Decimal('0')
            self.price_eur = Decimal('0')
            self.price_uah = Decimal('0')

        super().save(*args, **kwargs)  # Вызов стандартного метода save

    class Meta:
        db_table = 'listings'


