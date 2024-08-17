from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import UpdateAPIView, CreateAPIView,\
    ListAPIView, DestroyAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
import django_filters
from django.db.models import Avg

from cars.filters import CarFilter
from cars.models import CarModel
from core.pagination import PagePagination


from core.permissions import IsSeller,  IsPremiumSeller, IsManager, IsSellerOrManagerAndOwner

from .serializers import ListingPhotoSerializer, ListingCreateSerializer,\
    ListingUpdateSerializer, PremiumStatsSerializer, ListingListSerializer
from .models import ListingModel
from .filters import ListingFilter

class ListingAddPhotoAPIView(UpdateAPIView):
    permission_classes = (IsSeller,)
    serializer_class = ListingPhotoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        listing_id = self.kwargs.get('listing_id')
        return get_object_or_404(ListingModel, id=listing_id)

    def perform_update(self, serializer):
        listing = self.get_object()
        if listing.listing_photo:
            listing.listing_photo.delete()
        super().perform_update(serializer)



class ListingCreateView(CreateAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsSeller]

class ListingUpdateView(UpdateAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingUpdateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == 'seller':
            return ListingModel.objects.filter(seller=user)
        return ListingModel.objects.all()


class ListingDeleteView(DestroyAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsSeller, IsManager]

    def get_object(self):
        obj = super().get_object()
        if obj.seller != self.request.user:
            raise PermissionDenied("You do not have permission to delete this listing.")
        return obj


class ListingListView(ListAPIView):
    permission_classes = [AllowAny]
    pagination_class = PagePagination
    queryset = ListingModel.objects.select_related('car').order_by('-created_at')
    serializer_class = ListingListSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ListingFilter


class PremiumStatsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsPremiumSeller]

    def get(self, request, *args, **kwargs):
        listing_id = kwargs.get('listing_id')
        listing = ListingModel.objects.filter(id=listing_id).select_related('car').first()
        if not listing:
            return Response({'error': 'Listing not found'}, status=404)

        # Применяем CarFilter для фильтрации по автомобилям
        car_filter = CarFilter(request.GET, queryset=CarModel.objects.all())
        cars = car_filter.qs

        # Фильтрация объявлений по автомобилям и региону
        listings = ListingModel.objects.filter(car__in=cars, region=listing.region)
        region_avg_price = listings.aggregate(Avg('price_usd'))['price_usd__avg']  # Предполагаем, что цены уже в USD
        country_avg_price = ListingModel.objects.filter(car__in=cars).aggregate(Avg('price_usd'))['price_usd__avg']

        return Response({
            'views_data': {
                'total_views': listing.views_day + listing.views_week + listing.views_month,  # Суммарные просмотры
                'views_day': listing.views_day,
                'views_week': listing.views_week,
                'views_month': listing.views_month,
            },
            'average_price_by_region': region_avg_price,
            'average_price_by_country': country_avg_price
        })
