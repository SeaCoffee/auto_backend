from django.db import models
from django.db.transaction import atomic
from django.contrib.auth import get_user_model

from cars.models import CarModel, Brand, ModelName
from core.services.managers_notification import ManagerNotificationService
from currency.models import CurrencyModel
from core.enums.profanity_enum import ProfanityFilter
from core.services.errors import ValidationErrors, CustomValidationError


class ListingManager(models.Manager):

    @atomic()
    def create_listing(self, validated_data, seller):
        errors = ValidationErrors()

        # Проверка бренда и модели
        brand = validated_data.pop('brand', None)
        model_name = validated_data.pop('model_name', None)
        body_type = validated_data.pop('body_type', None)

        if not Brand.objects.filter(id=brand.id).exists():
            errors.add_error("brand", "Selected brand does not exist.")

        if not ModelName.objects.filter(id=model_name.id, brand=brand).exists():
            errors.add_error("model_name", "Model does not exist under this brand.")

        if errors.has_errors():
            raise CustomValidationError("Validation errors: " + str(errors.get_errors()))

        car_model, created = CarModel.objects.get_or_create(
            brand=brand,
            model_name=model_name,
            body_type=body_type
        )

        currency = validated_data.get('currency')
        current_rate = CurrencyModel.objects.filter(currency_code=currency.currency_code).order_by(
            '-updated_at').first()
        initial_currency_rate = current_rate.rate if current_rate else None

        # Создаем объявление с полем `active=False`
        listing = self.create(
            car=car_model,
            seller=seller,
            year=validated_data.get('year'),
            engine=validated_data.get('engine'),
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            listing_photo=validated_data.get('listing_photo'),
            price=validated_data.get('price'),
            currency=currency,
            initial_currency_rate=initial_currency_rate,
            region=validated_data.get('region'),
            active=False  # По умолчанию объявление неактивно
        )

        # Проверяем на наличие ненормативной лексики
        if ProfanityFilter.is_profane(listing.description):
            listing.edit_attempts += 1
            listing.save()

            if listing.edit_attempts >= 3:
                # Если 3 попытки, то деактивируем объявление и уведомляем менеджера
                managers = get_user_model().objects.filter(role_id=3)
                for manager in managers:
                    ManagerNotificationService.send_profanity_notification(
                        description=listing.description,
                        username=seller.username,
                        manager=manager
                    )
                listing.active = False
                listing.save()
                raise CustomValidationError("Maximum edit attempts exceeded. The listing has been deactivated.")

            # Ошибка для пользователя, если обнаружен мат
            raise CustomValidationError("The description contains prohibited words. Please edit and resubmit.")

        # Если все проверки пройдены, делаем объявление активным
        listing.active = True
        listing.save()

        return listing

