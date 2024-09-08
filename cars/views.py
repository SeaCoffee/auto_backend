from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status

from .serializers import CarSerializer, BrandSerializer, ModelNameSerializer
from .models import CarModel, Brand, ModelName
from core.pagination import PagePagination
from .filters import CarFilter



class CarListCreateView(ListCreateAPIView):
    """
    Вью для получения списка автомобилей и создания нового автомобиля.
    Наследуется от ListCreateAPIView, что предоставляет методы GET и POST.
    """

    # Устанавливаем queryset для получения всех объектов CarModel.
    queryset = CarModel.objects.all()

    # Определяем, что для сериализации данных используется CarSerializer.
    serializer_class = CarSerializer

    # Указываем, что доступ к представлению разрешен любому пользователю.
    permission_classes = [AllowAny]

    # Указываем класс пагинации, который будет использован для отображения списка автомобилей.
    pagination_class = PagePagination

    # Фильтрация и сортировка данных.
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # Определяем фильтр, который будет использоваться для фильтрации автомобилей.
    filterset_class = CarFilter

    # Поля, по которым можно сортировать список автомобилей.
    ordering_fields = ['year', 'brand', 'model_name']

    # Поле сортировки по умолчанию - год выпуска автомобиля.
    ordering = ['year']


class CarRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Вью для получения, обновления и удаления конкретного автомобиля по его ID.
    Наследуется от RetrieveUpdateDestroyAPIView, что предоставляет методы GET, PUT, PATCH и DELETE.
    """

    # Устанавливаем queryset для получения всех объектов CarModel.
    queryset = CarModel.objects.all()

    # Определяем, что для сериализации данных используется CarSerializer.
    serializer_class = CarSerializer

    # Доступ к представлению разрешен любому пользователю.
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        """
        Метод для удаления конкретного автомобиля по его ID.
        После успешного удаления возвращает сообщение с кодом 204 (No Content).
        """
        # Получаем объект автомобиля для удаления.
        instance = self.get_object()

        # Удаляем объект из базы данных.
        self.perform_destroy(instance)

        # Возвращаем сообщение об успешном удалении.
        return Response({"detail": "Car successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


class BrandModelDataView(ListAPIView):
    """
    Вью для получения данных о брендах и связанных с ними моделях автомобилей.
    Наследуется от ListAPIView и поддерживает метод GET.
    """
    # Определяем, какие данные будем выводить
    queryset = Brand.objects.all()

    # Используем сериализатор для брендов
    serializer_class = BrandSerializer

    # Доступ к представлению разрешен любому пользователю
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Переопределяем метод list для добавления данных о моделях, связанных с брендами.
        """
        brands = Brand.objects.all()
        response = BrandSerializer(brands, many=True).data

        # Создаем правильную структуру для брендов и моделей
        brands_models = {}
        for brand in brands:
            models = ModelName.objects.filter(brand=brand)
            brands_models[brand.id] = ModelNameSerializer(models, many=True).data

        # Объединяем данные сериализатора с моделями автомобилей
        return Response({
            'brands': response,
            'brands_models': brands_models  # здесь словарь, где ключ — это ID бренда
        })


