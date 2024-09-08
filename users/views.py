from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView, CreateAPIView,\
    UpdateAPIView, RetrieveAPIView,DestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.http import Http404


from .serializers import UserSerializer, UpgradeAccountSerializer, ProfileSerializer,  \
    ProfileAvatarSerializer, BlacklistSerializer, ManagerSerializer, UserDetailSerializer
from .models import UserModel, ProfileModel, BlacklistModel
from core.permissions import IsManager

from django.contrib.auth import get_user_model

class UserCreateAPIView(CreateAPIView):
    """
    Представление для создания нового пользователя.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Разрешен доступ для всех.


class ProfileDetailView(RetrieveAPIView):
    """
    Представление для получения информации о профиле пользователя.
    """
    queryset = ProfileModel.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]  # Требуется аутентификация.

    def get_object(self):
        """
        Переопределенный метод для получения профиля текущего пользователя.
        """
        try:
            return self.request.user.profile  # Возвращаем профиль текущего пользователя.
        except UserModel.profile.RelatedObjectDoesNotExist:
            raise Http404("No Profile found for this user.")  # Если профиль не найден, возвращаем 404.


class UpgradeAccountAPIView(UpdateAPIView, GenericViewSet):
    """
    Представление для обновления типа аккаунта пользователя до премиум.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UpgradeAccountSerializer
    permission_classes = [IsAuthenticated]  # Требуется аутентификация.

    @action(detail=False, methods=['put'])
    def update(self, request, *args, **kwargs):
        """
        Метод для обновления аккаунта.
        """
        user = request.user  # Текущий пользователь.
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Сохраняем обновленные данные.
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateManagerView(CreateAPIView):
    """
    Представление для создания менеджера (доступно только администраторам).
    """
    permission_classes = [IsAdminUser]  # Доступно только администраторам.
    serializer_class = ManagerSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)  # Используем стандартный метод POST.


class UserAddAvatarAPIView(UpdateAPIView):
    """
    Представление для добавления аватара пользователя.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileAvatarSerializer
    parser_classes = (MultiPartParser, FormParser)  # Для обработки изображений.

    def get_object(self):
        return self.request.user.profile  # Возвращаем профиль текущего пользователя.

    def update(self, request, *args, **kwargs):
        """
        Метод для обновления аватара.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Сохраняем аватар.
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)  # Для отладки выводим ошибки.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteSelfView(DestroyAPIView):
    """
    Представление для удаления учетной записи пользователя.
    """
    permission_classes = [IsAuthenticated]  # Доступно только аутентифицированным пользователям.

    def delete(self, request, *args, **kwargs):
        """
        Метод для удаления учетной записи.
        """
        print("Delete method called")  # Выводим отладочное сообщение.
        user = request.user
        user.delete()  # Удаляем пользователя.
        return Response({"detail": "Your account has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AddToBlacklistView(GenericAPIView):
    """
    Представление для добавления или удаления пользователей из черного списка.
    """
    permission_classes = [IsAuthenticated, IsManager]  # Требуется аутентификация и права менеджера.

    def post(self, request, *args, **kwargs):
        """
        Метод для добавления пользователя в черный список.
        """
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', '')
        try:
            user_to_blacklist = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if BlacklistModel.objects.filter(user=user_to_blacklist).exists():
            return Response({"detail": "User is already in blacklist."}, status=status.HTTP_400_BAD_REQUEST)

        blacklist_entry = BlacklistModel.objects.create(user=user_to_blacklist, added_by=request.user, reason=reason)
        serializer = BlacklistSerializer(blacklist_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Метод для удаления пользователя из черного списка.
        """
        user_id = request.data.get('user_id')
        try:
            blacklist_entry = BlacklistModel.objects.get(user__pk=user_id)
            blacklist_entry.delete()
            return Response({"detail": "User removed from blacklist."}, status=status.HTTP_204_NO_CONTENT)
        except BlacklistModel.DoesNotExist:
            return Response({"detail": "User not found in blacklist."}, status=status.HTTP_404_NOT_FOUND)


class CurrentUsereDetailsView(RetrieveAPIView):
    """
    Представление для получения данных текущего пользователя.
    """
    permission_classes = [IsAuthenticated]  # Доступно только аутентифицированным пользователям.

    def get(self, request):
        """
        Метод для получения информации о текущем пользователе.
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)  # Возвращаем информацию о пользователе.
