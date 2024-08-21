from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView, CreateAPIView,\
    UpdateAPIView, RetrieveAPIView,DestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from django.http import Http404


from .serializers import UserSerializer, UpgradeAccountSerializer, ProfileSerializer,  \
    ProfileAvatarSerializer, BlacklistSerializer, ManagerSerializer, UserDetailSerializer
from .models import UserModel, ProfileModel, BlacklistModel
from core.permissions import IsManager


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ProfileDetailView(RetrieveAPIView):
    queryset = ProfileModel.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.profile
        except UserModel.profile.RelatedObjectDoesNotExist:
            raise Http404("No Profile found for this user.")


class UpgradeAccountAPIView(GenericViewSet, UpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UpgradeAccountSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['put'])
    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateManagerView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ManagerSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserAddAvatarAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileAvatarSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user.profile

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)  # Debugging info
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserDeleteSelfView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        print("Delete method called")  # Добавьте отладочное сообщение
        user = request.user
        user.delete()
        return Response({"detail": "Your account has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AddToBlacklistView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, *args, **kwargs):
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
        user_id = request.data.get('user_id')
        try:
            blacklist_entry = BlacklistModel.objects.get(user__pk=user_id)
            blacklist_entry.delete()
            return Response({"detail": "User removed from blacklist."}, status=status.HTTP_204_NO_CONTENT)
        except BlacklistModel.DoesNotExist:
            return Response({"detail": "User not found in blacklist."}, status=status.HTTP_404_NOT_FOUND)


class CurrentUsereDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)