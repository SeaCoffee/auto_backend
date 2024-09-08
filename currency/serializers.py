from rest_framework import serializers

from .models import CurrencyModel

class CurrencySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели `CurrencyModel`. Определяет поля, которые будут сериализованы для API.
    """

    class Meta:
        model = CurrencyModel  # Указываем модель для сериализации.
        fields = ['id', 'currency_code', 'rate', 'created_at', 'updated_at']  # Поля, которые будут возвращаться через API.
