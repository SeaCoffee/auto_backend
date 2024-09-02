from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import ListingModel
from cars.models import CarModel
from users.models import UserModel
from core.enums.profanity_enum import ProfanityFilter
from core.services.email_service import EmailService
from cars.serializers import CarSerializer
from core.services.managers_notification import ManagerNotificationService
from currency.models import CurrencyModel
from cars.serializers import CarSerializer, Brand, ModelName
from core.enums.country_region_enum import Region
from django.contrib.auth import get_user_model


import logging
logger = logging.getLogger(__name__)

class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingModel
        fields = ['listing_photo']

    def validate_listings_photo(self, photo):
        max_size = 100 * 1024
        if photo.size > max_size:
            raise ValidationError('Maximum size of 100KB exceeded')
        return photo

class ListingCreateSerializer(serializers.ModelSerializer):
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
            'currency', 'region'
        )

    def validate_description(self, value):
        instance = self.instance
        if ProfanityFilter.is_profane(value):
            if instance:
                instance.edit_attempts += 1
                instance.save()
                if instance.edit_attempts >= 3:
                    instance.active = False
                    instance.save()
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

    def validate(self, data):
        print("Валидация данных:", data)
        request = self.context.get('request')
        seller = request.user

        if seller.account_type == 'basic' and ListingModel.objects.filter(seller=seller).count() >= 1:
            print("Превышен лимит для базового аккаунта")
            raise serializers.ValidationError("Basic account holders can only create one listing.")

        brand = data.get('brand')
        model_name = data.get('model_name')

        if not ModelName.objects.filter(brand=brand, id=model_name.id).exists():
            print(f"Модель {model_name} не найдена под брендом {brand}")
            raise serializers.ValidationError("Car model with specified details does not exist.")

        print("Данные валидны")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        print('request')
        seller = request.user
        listing_photo = validated_data.pop('listing_photo', None)

        listing = ListingModel.objects.create_listing(validated_data, seller)  # Вызов создания объявления

        if listing_photo:
            listing.listing_photo = listing_photo  # Сохранение фотографии если она есть
            listing.save()

        return listing


class ListingDetailSerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    body_type = serializers.SerializerMethodField()
    currency_display = serializers.CharField(source='currency.currency_code', read_only=True)

    class Meta:
        model = ListingModel
        fields = (
            'id', 'brand', 'model_name', 'body_type', 'year', 'engine', 'title', 'description', 'listing_photo',
            'price', 'currency_display', 'region', 'seller', 'created_at', 'price_usd', 'price_eur', 'price_uah'
        )

    def get_brand(self, obj):
        return obj.car.brand.name

    def get_model_name(self, obj):
        return obj.car.model_name.name

    def get_body_type(self, obj):
        return obj.car.body_type



class ListingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingModel
        fields = ['title', 'description', 'price', 'currency', 'listing_photo']

    def validate_description(self, value):
        instance = self.instance
        if ProfanityFilter.is_profane(value):
            instance.edit_attempts += 1
            instance.save()
            if instance.edit_attempts >= 3:
                instance.active = False
                instance.save()

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
        instance = super().update(instance, validated_data)
        instance.active = True
        instance.save()
        return instance


class PremiumStatsSerializer(serializers.Serializer):
    total_views = serializers.IntegerField()
    views_day = serializers.IntegerField()
    views_week = serializers.IntegerField()
    views_month = serializers.IntegerField()
    average_price_by_region = serializers.FloatField(allow_null=True)
    average_price_by_country = serializers.FloatField(allow_null=True)

class ListingListSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)

    class Meta:
        model = ListingModel
        fields = ['id', 'title', 'description', 'listing_photo', 'active', 'car']
