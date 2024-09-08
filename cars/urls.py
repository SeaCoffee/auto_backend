from django.urls import path
from .views import BrandModelDataView, CarListCreateView, CarRetrieveUpdateDestroyView

# Определение маршрутов для обработки запросов, связанных с автомобилями и данными брендов/моделей.
urlpatterns = [
    # Маршрут для получения списка автомобилей и создания нового автомобиля.
    path('', CarListCreateView.as_view(), name='cars-list-create'),

    # Маршрут для создания нового автомобиля через отдельный URL.
    path('car/create/', CarListCreateView.as_view(), name='car-create'),

    # Маршрут для получения, обновления или удаления конкретного автомобиля по его ID (pk).
    path('car/<int:pk>/', CarRetrieveUpdateDestroyView.as_view(), name='car-detail'),

    # Маршрут для получения данных о брендах и моделях.
    path('data/', BrandModelDataView.as_view(), name='brand-model-data'),
]
