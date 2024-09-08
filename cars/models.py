from django.db import models
from django.core.exceptions import ValidationError

from core.models import BaseModel


class Brand(BaseModel):
    """
    Brand - это модель, представляющая автомобильный бренд.
    Наследуется от BaseModel, что добавляет общие поля даты создания/изменения.
    """

    # Поле 'name' хранит название бренда. Максимальная длина - 50 символов.
    name = models.CharField(max_length=50)

    class Meta:
        # Определяет имя таблицы в базе данных как 'brand'.
        db_table = 'brand'


class ModelName(BaseModel):
    """
    ModelName - это модель, представляющая конкретную модель автомобиля, связанную с брендом.
    """

    # Связь с моделью Brand через ForeignKey. related_name позволяет получить все модели бренда (Brand.models).
    brand = models.ForeignKey(Brand, related_name='models', on_delete=models.CASCADE)

    # Поле 'name' хранит название модели автомобиля. Максимальная длина - 50 символов.
    name = models.CharField(max_length=50)

    class Meta:
        # Имя таблицы в базе данных будет 'model_name'.
        db_table = 'model_name'


class CarModel(BaseModel):
    """
    CarModel - это модель, представляющая конкретный автомобиль с указанием типа кузова, модели и бренда.
    """

    # Предопределенные варианты типов кузова автомобиля. Выбираются из набора заранее заданных типов.
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

    # Связь с моделью Brand через ForeignKey. Если бренд удаляется, автомобиль тоже удаляется (CASCADE).
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    # Связь с моделью ModelName через ForeignKey. related_name='cars' позволяет получить все автомобили модели.
    # Поле допускает null-значения, если модель автомобиля не указана.
    model_name = models.ForeignKey(ModelName, related_name='cars', on_delete=models.CASCADE, null=True)

    # Поле 'body_type' хранит тип кузова автомобиля, который выбирается из предопределенных вариантов BODY_TYPES.
    body_type = models.CharField(max_length=50, choices=BODY_TYPES)

    def clean(self):
        """
        Метод clean используется для валидации данных перед сохранением.
        Проверяет, что год выпуска автомобиля находится в диапазоне 1885-2024,
        а объем двигателя находится в пределах от 0.1 до 20 литров.
        """
        super().clean()
        if not (1885 <= self.year <= 2024):
            raise ValidationError({'year': "Year must be between 1885 and 2024."})
        if not (0.1 <= float(self.engine) <= 20):
            raise ValidationError({'engine': "Engine size must be between 0.1 and 20 liters."})

    class Meta:
        # Имя таблицы в базе данных - 'cars'.
        db_table = 'cars'
