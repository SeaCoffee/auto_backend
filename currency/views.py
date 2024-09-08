from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CurrencyModel
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CurrencySerializer

class CurrencyAPIView(APIView):
    """
    APIView для работы с валютами. Позволяет получать список всех валют и их курсов.
    """

    # Устанавливаем, что доступ к API разрешен для всех.
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Обрабатывает GET-запрос для получения списка валют и их курсов.
        :param request: Запрос от клиента
        :return: Сериализованные данные валют
        """
        currencies = CurrencyModel.objects.all()  # Получаем все записи валют.
        serializer = CurrencySerializer(currencies, many=True)  # Сериализуем данные.
        return Response(serializer.data)  # Возвращаем данные в формате JSON.