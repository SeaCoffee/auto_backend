from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import ListingModel
from cars.models import CarModel
from users.models import UserModel
from core.enums.profanity_enum import ProfanityFilter
from core.services.email_service import EmailService
from core.services.managers_notification import ManagerNotificationService
from currency.models import CurrencyModel
from cars.serializers import CarSerializer
from cars.models import Brand, ModelName
from core.enums.country_region_enum import Region
from core.services.errors import CustomValidationError

from django.contrib.auth import get_user_model


class ListingPhotoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки фотографий в объявлениях. Включает валидацию на размер загружаемого файла.
    """
    class Meta:
        model = ListingModel
        fields = ['listing_photo']

    def validate_listings_photo(self, photo):
        """
        Проверка на максимальный размер фотографии (100KB).
        """
        max_size = 100 * 1024  # Максимальный размер файла в байтах.
        if photo.size > max_size:
            raise ValidationError('Maximum size of 100KB exceeded')  # Ошибка, если файл превышает 100KB.
        return photo


class ListingCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания объявления. Включает валидацию и обработку полей, таких как бренд, модель, кузов, регион и фотография.
    """
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), write_only=True)
    model_name = serializers.PrimaryKeyRelatedField(queryset=ModelName.objects.all(), write_only=True)
    body_type = serializers.ChoiceField(choices=CarModel.BODY_TYPES, write_only=True)
    currency = serializers.PrimaryKeyRelatedField(queryset=CurrencyModel.objects.all())
    region = serializers.ChoiceField(choices=[(region.value, region.value) for region in Region])
    listing_photo = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = ListingModel
        fields = (
            'brand', 'model_name', 'body_type', 'year', 'engine', 'title', 'description', 'listing_photo', 'price',
            'currency', 'region', 'initial_currency_rate', 'active'
        )

    def create(self, validated_data):
        """
        Метод для создания нового объявления. Включает валидацию данных и сохранение фотографии.
        """
        request = self.context.get('request')
        seller = request.user

        try:
            # Передаем все validated_data, включая brand, model_name и body_type, в менеджер.
            listing = ListingModel.objects.create_listing(validated_data, seller)

            # Обновляем фотографию, если она есть.
            listing_photo = validated_data.get('listing_photo', None)
            if listing_photo:
                listing.listing_photo = listing_photo
                listing.save()

        except CustomValidationError as e:
            # Возвращаем ошибки, если возникла ошибка валидации.
            raise serializers.ValidationError({"errors": e.message})

        return listing


class ListingDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра объявления. Включает дополнительные поля для бренда, модели и курса валют.
    """
    brand = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    body_type = serializers.SerializerMethodField()
    current_currency_rate = serializers.SerializerMethodField()

    class Meta:
        model = ListingModel
        fields = (
            'id', 'brand', 'model_name', 'body_type', 'year', 'engine', 'title', 'description', 'listing_photo', 'price',
            'currency', 'region', 'seller', 'initial_currency_rate', 'current_currency_rate'
        )

    def get_brand(self, obj):
        """
        Получение ID бренда автомобиля.
        """
        return obj.car.brand.id

    def get_model_name(self, obj):
        """
        Получение ID модели автомобиля.
        """
        return obj.car.model_name.id

    def get_body_type(self, obj):
        """
        Получение типа кузова автомобиля.
        """
        return obj.car.body_type

    def get_current_currency_rate(self, obj):
        """
        Получение текущего курса валюты для объявления.
        """
        current_rate = CurrencyModel.objects.filter(currency_code=obj.currency.currency_code).order_by('-updated_at').first()
        if current_rate:
            return current_rate.rate
        return None


class ListingUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления объявления. Включает валидацию описания и обновление активного статуса.
    """
    class Meta:
        model = ListingModel
        fields = ['title', 'description', 'price', 'currency', 'listing_photo']

    def validate_description(self, value):
        """
        Валидация описания на наличие ненормативной лексики.
        """
        instance = self.instance
        if ProfanityFilter.is_profane(value):
            instance.edit_attempts += 1
            instance.save()
            if instance.edit_attempts >= 3:
                # Деактивируем объявление после 3 неудачных попыток редактирования.
                instance.active = False
                instance.save()

                # Отправляем уведомления менеджерам о нарушении.
                seller = instance.seller
                managers = get_user_model().objects.filter(role_id=3)
                for manager in managers:
                    ManagerNotificationService.send_profanity_notification(
                        description=value,
                        username=seller.username,
                        manager=manager
                    )
                raise serializers.ValidationError("Maximum edit attempts exceeded. The listing has been deactivated.")
            raise serializers.ValidationError("The description contains prohibited words.")
        return value

    def update(self, instance, validated_data):
        """
        Обновление объявления. Если фото не передано, возвращаем ошибку, но не вылетаем.
        """
        listing_photo = validated_data.get('listing_photo', None)

        # Проверяем, было ли передано новое фото
        if not listing_photo:
            raise serializers.ValidationError({"listing_photo": "Photo is required for updating the listing."})

        # Если фото было передано, обновляем его
        instance = super().update(instance, validated_data)
        instance.active = True  # Активируем объявление после обновления.
        instance.save()
        return instance



class PremiumStatsSerializer(serializers.Serializer):
    """
    Сериализатор для отображения статистики для премиум-аккаунтов.
    """
    total_views = serializers.IntegerField()
    views_day = serializers.IntegerField()
    views_week = serializers.IntegerField()
    views_month = serializers.IntegerField()
    average_price_by_region = serializers.FloatField(allow_null=True)
    average_price_by_country = serializers.FloatField(allow_null=True)


class ListingListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого списка объявлений. Включает информацию о машине и статусе объявления.
    """
    car = CarSerializer(read_only=True)

    class Meta:
        model = ListingModel
        fields = ['id', 'title', 'description', 'listing_photo', 'active', 'car']
