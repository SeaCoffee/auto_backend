from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from .models import CarModel, Brand, ModelName
from core.services.managers_notification import ManagerNotificationService


class CarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и валидации объекта CarModel.
    """

    # Поле для связи с брендом автомобиля. PrimaryKeyRelatedField связывает автомобиль с существующим объектом Brand.
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())

    # Поле для связи с моделью автомобиля. PrimaryKeyRelatedField связывает автомобиль с существующим объектом ModelName.
    model_name = serializers.PrimaryKeyRelatedField(queryset=ModelName.objects.all())

    class Meta:
        # Указывает, что сериализатор работает с моделью CarModel.
        model = CarModel
        # Поля, которые будут сериализованы.
        fields = ['id', 'brand', 'model_name', 'body_type']

    def create(self, validated_data):
        """
        Метод создания объекта CarModel с дополнительной валидацией.
        Проверяет, что указанная модель автомобиля принадлежит указанному бренду.
        Если модель не принадлежит бренду, отправляется уведомление менеджеру и выбрасывается ошибка.
        """
        brand = validated_data.get('brand')
        model_name_id = validated_data.get('model_name').id

        # Проверка, существует ли связь между брендом и моделью.
        if not ModelName.objects.filter(id=model_name_id, brand=brand).exists():
            # Получаем текущего пользователя из контекста запроса.
            user = self.context['request'].user
            # Получаем объект ModelName по id.
            model_name = ModelName.objects.get(id=model_name_id)
            # Отправляем уведомление менеджеру.
            self.send_manager_notification(brand.name, model_name.name, user)
            # Генерируем ошибку валидации, если связь между брендом и моделью не найдена.
            raise serializers.ValidationError("Brand or model does not exist. Notification sent to manager.")

        # Если все проверки прошли успешно, создаем объект CarModel.
        return CarModel.objects.create(**validated_data)

    def send_manager_notification(self, brand_name, model_name, user):
        """
        Отправляет уведомление менеджеру, если бренд и модель не совпадают.
        """
        UserModel = get_user_model()  # Получаем модель пользователя (вероятно, кастомная).
        try:
            # Ищем пользователя с ролью менеджера (role_id=3).
            manager = UserModel.objects.filter(role_id=3).first()
            if manager:
                # Отправляем уведомление с использованием сервиса уведомлений.
                ManagerNotificationService.send_notification(brand_name, model_name, user.username, manager.id)
            else:
                # Если менеджер не найден, выбрасывается ошибка.
                raise serializers.ValidationError("Manager not found.")
        except ObjectDoesNotExist:
            # Обработка исключений, если менеджер не существует в базе данных.
            raise serializers.ValidationError("Manager not found.")


class CarListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения списка автомобилей.
    """

    # Поля для отображения названия бренда и модели, связанные через SlugRelatedField.
    brand = serializers.SlugRelatedField(slug_field='name', read_only=True)
    model_name = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        # Указывает, что сериализатор работает с моделью CarModel.
        model = CarModel
        # Поля, которые будут включены в список.
        fields = ['id', 'brand', 'model_name', 'year', 'body_type', 'engine']


class BrandSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с объектами Brand.
    """

    class Meta:
        # Указывает, что сериализатор работает с моделью Brand.
        model = Brand
        # Поля, которые будут сериализованы.
        fields = ['id', 'name']


class ModelNameSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с объектами ModelName.
    """

    # Поле для отображения бренда модели, используя SlugRelatedField.
    brand = serializers.SlugRelatedField(slug_field='name', queryset=Brand.objects.all())

    class Meta:
        # Указывает, что сериализатор работает с моделью ModelName.
        model = ModelName
        # Поля, которые будут сериализованы.
        fields = ['id', 'brand', 'name']




