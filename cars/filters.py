import django_filters
from django_filters import FilterSet

from .models import CarModel, Brand, ModelName


class CarFilter(FilterSet):
    """
    CarFilter - это фильтр, который помогает фильтровать автомобили по различным полям.
    Наследуется от FilterSet библиотеки django-filter.
    """

    # Фильтр по бренду автомобиля. Использует ModelChoiceFilter для выбора одного из существующих брендов.
    # 'field_name' указывает, что фильтр будет применен к полю 'brand' в модели.
    # queryset указывает на все доступные объекты Brand.
    # 'to_field_name' устанавливает, что при фильтрации будет использоваться поле 'id'.
    brand = django_filters.ModelChoiceFilter(
        field_name="brand",
        queryset=Brand.objects.all(),
        label='Бренд',
        to_field_name='id'
    )

    # Фильтр по названию модели автомобиля. Также использует ModelChoiceFilter.
    # 'field_name' указывает, что фильтрация будет применяться к полю 'model_name'.
    # queryset содержит все доступные модели автомобилей (ModelName).
    model_name = django_filters.ModelChoiceFilter(
        field_name="model_name",
        queryset=ModelName.objects.all(),
        label='Модель',
        to_field_name='id'
    )

    # Фильтр по типу кузова автомобиля. Использует ChoiceFilter для выбора одного из доступных вариантов.
    # 'field_name' указывает на поле 'body_type', а choices ссылается на предопределенные типы кузова (BODY_TYPES).
    body_type = django_filters.ChoiceFilter(
        field_name="body_type",
        choices=CarModel.BODY_TYPES,
        label='Тип кузова'
    )

    # Фильтр по двигателю автомобиля. Использует CharFilter для поиска по частичному совпадению (icontains).
    # Это позволяет находить записи, где поле 'engine' содержит введенные пользователем символы.
    engine = django_filters.CharFilter(field_name="engine", lookup_expr='icontains', label='Двигатель')

    class Meta:
        # Указывает, что фильтры будут применяться к модели CarModel.
        model = CarModel
        # Поля, которые будут использоваться для фильтрации в интерфейсе.
        fields = ['brand', 'model_name', 'body_type', 'engine']
