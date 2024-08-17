import django_filters
from django_filters import rest_framework as filters
from .models import ListingModel
from cars.models import CarModel



class ListingFilter(filters.FilterSet):
    brand = django_filters.CharFilter(field_name='car__brand')
    model_name = django_filters.CharFilter(field_name='car__model_name')
    min_year = django_filters.NumberFilter(field_name="car__year", lookup_expr='gte')
    max_year = django_filters.NumberFilter(field_name="car__year", lookup_expr='lte')
    body_type = django_filters.CharFilter(field_name="car__body_type")
    engine = django_filters.CharFilter(field_name="car__engine")

    region = django_filters.CharFilter(field_name='region')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = ListingModel
        fields = []

