import django_filters
from django_filters import FilterSet
from django_filters import rest_framework as filters
from django.db.models import Avg, Count
from django.http import QueryDict



from .models import CarModel


def car_filter(query: QueryDict):
    qs = CarModel.objects.all()

    brand = query.get('brand')
    model_name = query.get('model_name')

    if brand:
        qs = qs.filter(brand=brand)
    if model_name:
        qs = qs.filter(model_name=model_name)

    return qs



class CarFilter(FilterSet):
    min_year = django_filters.NumberFilter(field_name="year", lookup_expr='gte')
    max_year = django_filters.NumberFilter(field_name="year", lookup_expr='lte')
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr='icontains')
    model_name = django_filters.CharFilter(field_name="model_name__name", lookup_expr='icontains')
    body_type = django_filters.ChoiceFilter(field_name="body_type", choices=CarModel.BODY_TYPES)
    engine = django_filters.CharFilter(field_name="engine", lookup_expr='icontains')

    class Meta:
        model = CarModel
        fields = ['brand', 'model_name', 'body_type', 'engine', 'min_year', 'max_year']

