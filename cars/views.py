from rest_framework.generics import ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status

from .serializers import CarSerializer, BrandSerializer, ModelNameSerializer
from .models import CarModel, Brand, ModelName
from core.pagination import PagePagination



from .filters import CarFilter


class CarListCreateView(ListCreateAPIView):
    queryset = CarModel.objects.all()
    serializer_class = CarSerializer
    permission_classes = [AllowAny]
    pagination_class = PagePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CarFilter
    ordering_fields = ['year', 'brand', 'model_name']
    ordering = ['year']  # default ordering

class CarRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = CarModel.objects.all()
    serializer_class = CarSerializer
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Car successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

class BrandModelDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        brands = Brand.objects.all()
        models = ModelName.objects.all()

        brand_serializer = BrandSerializer(brands, many=True)
        model_serializer = ModelNameSerializer(models, many=True)

        return Response({
            'brands': brand_serializer.data,
            'models': model_serializer.data
        })