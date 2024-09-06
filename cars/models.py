from django.db import models
from django.core.exceptions import ValidationError

from core.models import BaseModel



class Brand(BaseModel):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'brand'


class ModelName(BaseModel):
    brand = models.ForeignKey(Brand, related_name='models', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'model_name'

class CarModel(BaseModel):
    BODY_TYPES = [
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('suv', 'SUV'),
        ('wagon', 'Wagon'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('minivan', 'Minivan'),
        ('pickup', 'Pickup'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model_name = models.ForeignKey(ModelName, related_name='cars', on_delete=models.CASCADE, null=True)
    body_type = models.CharField(max_length=50, choices=BODY_TYPES)


    def clean(self):
        super().clean()
        if not (1885 <= self.year <= 2024):
            raise ValidationError({'year': "Year must be between 1885 and 2024."})
        if not (0.1 <= float(self.engine) <= 20):
            raise ValidationError({'engine': "Engine size must be between 0.1 and 20 liters."})

    class Meta:
        db_table = 'cars'