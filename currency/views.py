from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CurrencyModel
from rest_framework.permissions import IsAuthenticated, AllowAny

class CurrencyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        currencies = CurrencyModel.objects.all()
        data = [{"id": currency.id, "code": currency.currency_code, "rate": currency.rate} for currency in currencies]
        return Response(data)
