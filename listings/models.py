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
    initial_currency_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, editable=False)

    objects = ListingManager()

    def save(self, *args, **kwargs):

        rates = CurrencyModel.objects.all().values('currency_code', 'rate')
        rates_dict = {rate['currency_code']: Decimal(rate['rate']) for rate in rates}


        base_rate = rates_dict.get(self.currency.currency_code, Decimal('1'))


        if base_rate != Decimal('0'):
            self.price_usd = (self.price / base_rate) * rates_dict.get('USD', Decimal('1'))
            self.price_eur = (self.price / base_rate) * rates_dict.get('EUR', Decimal('1'))
            self.price_uah = (self.price / base_rate) * rates_dict.get('UAH', Decimal('1'))
        else:

            self.price_usd = Decimal('0')
            self.price_eur = Decimal('0')
            self.price_uah = Decimal('0')


        super().save(*args, **kwargs)

    class Meta:
        db_table = 'listings'

    def increment_views(self):
        self.views_day += 1
        self.views_week += 1
        self.views_month += 1
        self.save(update_fields=['views_day', 'views_week', 'views_month'])


