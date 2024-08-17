from django.db import models
from core.models import BaseModel

class CurrencyModel(BaseModel):
    currency_code = models.CharField(max_length=3)
    rate = models.FloatField()

    class Meta:
        unique_together = ('currency_code', 'updated_at')
        db_table = 'currency'

