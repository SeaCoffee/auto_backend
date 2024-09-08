from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import UpdateAPIView, CreateAPIView,\
    ListAPIView, DestroyAPIView, RetrieveAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import django_filters
from django.db.models import Avg
from django.db.models import F, ExpressionWrapper, DecimalField
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.services.managers_notification import ManagerNotificationService
from cars.filters import CarFilter
from cars.models import CarModel
from core.pagination import PagePagination
from core.enums.country_region_enum import Region
from core.permissions import IsSeller,  IsPremiumSeller, IsManager, IsSellerOrManagerAndOwner
from .serializers import ListingPhotoSerializer, ListingCreateSerializer,\
    ListingUpdateSerializer, PremiumStatsSerializer, ListingListSerializer, ListingDetailSerializer
from .models import ListingModel
from .filters import ListingFilter
from core.services.errors import CustomValidationError, ValidationErrors

from django.contrib.auth import get_user_model


class ListingAddPhotoAPIView(UpdateAPIView):
    """
    Обновление фотографии для объявления.
    """
    permission_classes = (IsSeller,)
    serializer_class = ListingPhotoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        """
        Получение объявления по его ID.
        """
        listing_id = self.kwargs.get('listing_id')
        return get_object_or_404(ListingModel, id=listing_id)

    def perform_update(self, serializer):
        """
        Удаление предыдущей фотографии перед добавлением новой.
        """
        listing = self.get_object()
        if listing.listing_photo:
            listing.listing_photo.delete()
        super().perform_update(serializer)



class ListingCreateView(CreateAPIView):
    queryset = ListingModel.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsSeller]
    parser_classes = (MultiPartParser, FormParser)




class ListingUpdateView(UpdateAPIView):
    """
    Обновление объявления. Доступно продавцам и менеджерам.
    """
    queryset = ListingModel.objects.all()
    serializer_class = ListingUpdateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        """
        Продавцы могут обновлять только свои объявления, менеджеры имеют доступ ко всем.
        """
        user = self.request.user
        if user.role.name == 'seller':
            return ListingModel.objects.filter(seller=user)
        return ListingModel.objects.all()


class ListingDeleteView(DestroyAPIView):
    """
    Удаление объявления. Только продавец или менеджер может удалять.
    """
    queryset = ListingModel.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]

    def get_object(self):
        """
        Проверка, что текущий пользователь имеет право на удаление объявления.
        """
        obj = super().get_object()
        if obj.seller != self.request.user:
            raise PermissionDenied("You do not have permission to delete this listing.")
        return obj


class ListingListView(ListAPIView):
    """
    Список всех объявлений с возможностью фильтрации.
    """
    permission_classes = [AllowAny]
    pagination_class = PagePagination
    queryset = ListingModel.objects.select_related('car').order_by('-created_at')
    serializer_class = ListingListSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ListingFilter


class PremiumStatsView(RetrieveAPIView):
    """
       Получение статистики по премиум объявлениям для продавцов с премиум аккаунтом.
       """
    permission_classes = [IsAuthenticated, IsPremiumSeller]

    def get(self, request, *args, **kwargs):
        """
              Возвращает просмотры объявления и средние цены по региону и стране.
              """
        listing_id = kwargs.get('listing_id')
        listing = ListingModel.objects.filter(id=listing_id).select_related('car', 'currency').first()
        if not listing:
            return Response({'error': 'Listing not found'}, status=404)

        car_filter = CarFilter(request.GET, queryset=CarModel.objects.all())
        cars = car_filter.qs

        # Рассчитываем среднюю цену по региону
        listings = ListingModel.objects.filter(car__in=cars, region=listing.region).annotate(
            price_in_usd=ExpressionWrapper(
                F('price') / F('currency__rate'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
        region_avg_price = listings.aggregate(Avg('price_in_usd'))['price_in_usd__avg']

        # Рассчитываем среднюю цену по стране
        country_avg_price = ListingModel.objects.filter(car__in=cars).annotate(
            price_in_usd=ExpressionWrapper(
                F('price') / F('currency__rate'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).aggregate(Avg('price_in_usd'))['price_in_usd__avg']

        # Формируем данные для сериализации
        stats_data = {
            'total_views': listing.views_day + listing.views_week + listing.views_month,
            'views_day': listing.views_day,
            'views_week': listing.views_week,
            'views_month': listing.views_month,
            'average_price_by_region': region_avg_price,
            'average_price_by_country': country_avg_price,
        }

        # Используем сериализатор для форматирования ответа
        serializer = PremiumStatsSerializer(stats_data)
        return Response(serializer.data)


class RegionsAPIView(ListAPIView):
    """
    API для получения списка регионов.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'regions': [(region.value, region.name) for region in Region]
        })


class UserListingsView(ListAPIView):
    """
    API для получения списка объявлений текущего пользователя.
    """
    serializer_class = ListingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает объявления, принадлежащие текущему пользователю.
        """
        return ListingModel.objects.filter(seller=self.request.user)


class ListingRetrieveView(RetrieveAPIView):
    """
    Получение подробной информации о объявлении.
    """
    queryset = ListingModel.objects.all()
    serializer_class = ListingUpdateSerializer
    permission_classes = [IsSellerOrManagerAndOwner]

    def get_queryset(self):
        """
        Продавцы могут получать доступ только к своим объявлениям, менеджеры ко всем.
        """
        user = self.request.user
        if user.role.name == 'seller':
            return ListingModel.objects.filter(seller=user)
        return ListingModel.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """
        Увеличение количества просмотров при каждом запросе на детали объявления.
        """
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ListingRetrieveDetailView(RetrieveAPIView):
    """
    Получение детализированных данных об объявлении, включая автомобиль.
    """
    queryset = ListingModel.objects.select_related('car')
    serializer_class = ListingDetailSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """
        Увеличение количества просмотров и возврат данных.
        """
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BrandRequestView(CreateAPIView):
    """
    API для отправки запроса на добавление нового бренда.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Отправка запроса менеджерам для добавления нового бренда.
        """
        brand_name = request.data.get('brand_name')
        if not brand_name:
            return Response({"error": "Название бренда обязательно"}, status=status.HTTP_400_BAD_REQUEST)

        username = request.user.username

        # Отправляем уведомление менеджерам о запросе на добавление бренда.
        ManagerNotificationService.send_notification(
            brand_name=brand_name,
            model_name=None,
            username=username
        )

        return Response({"message": "Запрос на добавление бренда отправлен менеджеру"}, status=status.HTTP_201_CREATED)

