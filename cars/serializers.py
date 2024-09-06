from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from .models import CarModel, Brand, ModelName
from core.services.managers_notification import ManagerNotificationService


class CarSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    model_name = serializers.PrimaryKeyRelatedField(queryset=ModelName.objects.all())

    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'model_name', 'body_type']

    def create(self, validated_data):
        brand = validated_data.get('brand')
        model_name_id = validated_data.get('model_name').id


        if not ModelName.objects.filter(id=model_name_id, brand=brand).exists():
            user = self.context['request'].user
            model_name = ModelName.objects.get(id=model_name_id)
            self.send_manager_notification(brand.name, model_name.name, user)
            raise serializers.ValidationError("Brand or model does not exist. Notification sent to manager.")

        return CarModel.objects.create(**validated_data)

    def send_manager_notification(self, brand_name, model_name, user):
        UserModel = get_user_model()
        try:
            manager = UserModel.objects.filter(role_id=3).first()
            if manager:
                ManagerNotificationService.send_notification(brand_name, model_name, user.username, manager.id)
            else:
                raise serializers.ValidationError("Manager not found.")
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Manager not found.")

class CarListSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(slug_field='name', read_only=True)
    model_name = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'model_name', 'year', 'body_type', 'engine']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class ModelNameSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(slug_field='name', queryset=Brand.objects.all())

    class Meta:
        model = ModelName
        fields = ['id', 'brand', 'name']




