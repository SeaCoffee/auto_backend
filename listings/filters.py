import django_filters
from .models import ListingModel
from cars.models import CarModel, Brand, ModelName
from core.enums.country_region_enum import Region


class ListingFilter(django_filters.FilterSet):
    """
    Фильтр для поиска и фильтрации объявлений. Использует cars фильтры для бренда, модели, типа кузова, года, региона и цены.
    """

    brand = django_filters.ModelChoiceFilter(
        field_name="car__brand",  # Связь с брендом автомобиля через модель машины.
        queryset=Brand.objects.all(),  # Список всех доступных брендов для фильтрации.
        label='Бренд',
        to_field_name='id'  # Фильтрация по ID бренда.
    )

    model_name = django_filters.ModelChoiceFilter(
        field_name="car__model_name",  # Связь с моделью автомобиля через модель машины.
        queryset=ModelName.objects.all(),  # Список всех доступных моделей для фильтрации.
        label='Модель',
        to_field_name='id'  # Фильтрация по ID модели.
    )

    body_type = django_filters.ChoiceFilter(
        field_name="car__body_type",  # Связь с типом кузова автомобиля через модель машины.
        choices=CarModel.BODY_TYPES,  # Список возможных типов кузова.
        label='Тип кузова'
    )

    min_year = django_filters.NumberFilter(field_name="year", lookup_expr='gte',
                                           label='Минимальный год')  # Фильтрация по минимальному году выпуска.
    max_year = django_filters.NumberFilter(field_name="year", lookup_expr='lte',
                                           label='Максимальный год')  # Фильтрация по максимальному году выпуска.

    region = django_filters.ChoiceFilter(
        field_name="region",  # Поле для фильтрации по региону.
        choices=Region.choices(),  # Список всех возможных регионов.
        label='Регион'
    )

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte',
                                            label='Минимальная цена')  # Фильтрация по минимальной цене.
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte',
                                            label='Максимальная цена')  # Фильтрация по максимальной цене.

    active = django_filters.BooleanFilter(field_name="active",
                                          label='Активные объявления')  # Фильтр по статусу объявления (активно/неактивно).

    class Meta:
        model = ListingModel  # Модель, к которой применяется фильтрация.
        fields = ['brand', 'model_name', 'body_type', 'min_year', 'max_year', 'region', 'price_min', 'price_max',
                  'active']  # Поля для фильтрации.

