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
from django.db.models import F, ExpressionWrapper, DecimalField


from cars.filters import CarFilter
from cars.models import CarModel
from core.pagination import PagePagination
from core.enums.country_region_enum import Region
from rest_framework.parsers import MultiPartParser, FormParser


from core.permissions import IsSeller,  IsPremiumSeller, IsManager, IsSellerOrManagerAndOwner

from .serializers import ListingPhotoSerializer, ListingCreateSerializer,\
    ListingUpdateSerializer, PremiumStatsSerializer, ListingListSerializer, ListingDetailSerializer
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
    parser_classes = (MultiPartParser, FormParser)
    queryset = ListingModel.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsSeller]


class ListingUpdateView(UpdateAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingUpdateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        if user.role.name == 'seller':
            return ListingModel.objects.filter(seller=user)
        return ListingModel.objects.all()


class ListingDeleteView(DestroyAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]

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
        listing = ListingModel.objects.filter(id=listing_id).select_related('car', 'currency').first()
        if not listing:
            return Response({'error': 'Listing not found'}, status=404)

        car_filter = CarFilter(request.GET, queryset=CarModel.objects.all())
        cars = car_filter.qs

        # Преобразование цен к USD для корректной агрегации
        listings = ListingModel.objects.filter(car__in=cars, region=listing.region).annotate(
            price_in_usd=ExpressionWrapper(
                F('price') / F('currency__rate'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        region_avg_price = listings.aggregate(Avg('price_in_usd'))['price_in_usd__avg']
        country_avg_price = ListingModel.objects.filter(car__in=cars).annotate(
            price_in_usd=ExpressionWrapper(
                F('price') / F('currency__rate'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).aggregate(Avg('price_in_usd'))['price_in_usd__avg']

        return Response({
            'views_data': {
                'total_views': listing.views_day + listing.views_week + listing.views_month,
                'views_day': listing.views_day,
                'views_week': listing.views_week,
                'views_month': listing.views_month,
            },
            'average_price_by_region': region_avg_price,
            'average_price_by_country': country_avg_price
        })


class RegionsAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            'regions': [(region.value, region.name) for region in Region]
        })


class UserListingsView(ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ListingModel.objects.filter(seller=self.request.user)


class ListingRetrieveView(RetrieveAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingUpdateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role.name == 'seller':
            return ListingModel.objects.filter(seller=user)
        return ListingModel.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ListingRetrieveDetailView(RetrieveAPIView):
    queryset = ListingModel.objects.select_related('car')
    serializer_class = ListingDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ListingModel.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
