from django.urls import path
from .views import CarListCreateView, CarRetrieveUpdateDestroyView, BrandModelDataView

urlpatterns = [
    #path('', CarListCreateView.as_view(), name='cars-list-create'),
    #path('car/create/', CarListCreateView.as_view(), name='car-create'),
    #path('car/<int:pk>/', CarRetrieveUpdateDestroyView.as_view(), name='car-detail'),
    path('data/', BrandModelDataView.as_view(), name='brand-model-data'),
]