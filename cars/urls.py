from django.urls import path
from .views import BrandModelDataView

urlpatterns = [
    path('data/', BrandModelDataView.as_view(), name='brand-model-data'),
]