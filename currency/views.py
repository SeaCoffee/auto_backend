from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CurrencyModel
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CurrencySerializer

class CurrencyAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        currencies = CurrencyModel.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data)
