from django.db import models
from django.db.transaction import atomic
from django.contrib.auth import get_user_model
from core.services.managers_notification import ManagerNotificationService
from cars.models import CarModel, Brand, ModelName
from core.enums.profanity_enum import ProfanityFilter
from rest_framework.exceptions import ValidationError as DRFValidationError

from currency.models import CurrencyModel



class ListingManager(models.Manager):

    @atomic()
    def create_listing(self, validated_data, seller):
        brand = validated_data.pop('brand')
        model_name = validated_data.pop('model_name')
        body_type = validated_data.pop('body_type')

        if not Brand.objects.filter(id=brand.id).exists():
            ManagerNotificationService.send_notification(
                brand_name=brand.name,
                model_name=None,
                username=seller.username
            )
            raise DRFValidationError("Brand does not exist. A request to add a new brand has been sent.")

        if not ModelName.objects.filter(id=model_name.id, brand=brand).exists():
            raise DRFValidationError("Model does not exist under this brand.")

        car_model, created = CarModel.objects.get_or_create(
            brand=brand,
            model_name=model_name,
            body_type=body_type
        )

        currency = validated_data.get('currency')
        current_rate = CurrencyModel.objects.filter(currency_code=currency.currency_code).order_by(
            '-updated_at').first()
        initial_currency_rate = current_rate.rate if current_rate else None

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
            active=False
        )

        listing.save()

        # Проверка на нецензурную лексику
        if ProfanityFilter.is_profane(listing.description):
            listing.edit_attempts += 1
            listing.save()
            if listing.edit_attempts >= 3:
                listing.active = False
                listing.save()
                managers = get_user_model().objects.filter(role_id=3)
                for manager in managers:
                    ManagerNotificationService.send_profanity_notification(
                        description=listing.description,
                        username=seller.username,
                        manager=manager
                    )
                raise DRFValidationError("Maximum edit attempts exceeded. The listing has been deactivated.")
            raise DRFValidationError("The description contains prohibited words. Please edit and resubmit.")


        print(f"Setting active to True for listing ID: {listing.id}")
        listing.active = True
        listing.save()

        print(f"Confirmed active status from database: {listing.active}")

        return listing



