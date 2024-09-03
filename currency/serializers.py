from rest_framework import serializers

from .models import CurrencyModel

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyModel
        fields = ['id', 'currency_code', 'rate', 'created_at', 'updated_at']
