import django_filters
from django_filters import FilterSet



from .models import CarModel, Brand, ModelName

class CarFilter(FilterSet):
    # Фильтры для модели CarModel

    brand = django_filters.ModelChoiceFilter(
        field_name="brand",
        queryset=Brand.objects.all(),
        label='Бренд',
        to_field_name='id'
    )

    model_name = django_filters.ModelChoiceFilter(
        field_name="model_name",
        queryset=ModelName.objects.all(),
        label='Модель',
        to_field_name='id'
    )

    body_type = django_filters.ChoiceFilter(
        field_name="body_type",
        choices=CarModel.BODY_TYPES,
        label='Тип кузова'
    )

    # Убраны фильтры по годам, так как они относятся к ListingModel
    engine = django_filters.CharFilter(field_name="engine", lookup_expr='icontains', label='Двигатель')

    class Meta:
        model = CarModel
        fields = ['brand', 'model_name', 'body_type', 'engine']
