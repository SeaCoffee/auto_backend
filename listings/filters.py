import django_filters
from .models import ListingModel
from cars.models import CarModel, Brand, ModelName
from core.enums.country_region_enum import Region



class ListingFilter(django_filters.FilterSet):
    brand = django_filters.ModelChoiceFilter(
        field_name="car__brand",
        queryset=Brand.objects.all(),
        label='Бренд',
        to_field_name='id'
    )

    model_name = django_filters.ModelChoiceFilter(
        field_name="car__model_name",
        queryset=ModelName.objects.all(),
        label='Модель',
        to_field_name='id'
    )

    body_type = django_filters.ChoiceFilter(
        field_name="car__body_type",
        choices=CarModel.BODY_TYPES,
        label='Тип кузова'
    )

    min_year = django_filters.NumberFilter(field_name="year", lookup_expr='gte', label='Минимальный год')
    max_year = django_filters.NumberFilter(field_name="year", lookup_expr='lte', label='Максимальный год')

    region = django_filters.ChoiceFilter(
        field_name="region",
        choices=Region.choices(),
        label='Регион'
    )

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte', label='Минимальная цена')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte', label='Максимальная цена')

    active = django_filters.BooleanFilter(field_name="active", label='Активные объявления')

    class Meta:
        model = ListingModel
        fields = ['brand', 'model_name', 'body_type', 'min_year', 'max_year', 'region', 'price_min', 'price_max', 'active']
