from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from users_auth.models import UserRoleModel
from core.services.email_service import EmailService
from .models import UserModel, ProfileModel, BlacklistModel
from django.apps import apps

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoleModel
        fields = ('id', 'name', 'created_at', 'updated_at')


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='user.role.name', read_only=True)
    account_type = serializers.CharField(source='user.account_type', read_only=True)

    class Meta:
        model = ProfileModel
        fields = ('id', 'name', 'surname', 'age', 'city', 'role', 'account_type')

class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = UserModel
        fields = ('username', 'role', 'account_type', 'profile')

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    role = serializers.PrimaryKeyRelatedField(queryset=UserRoleModel.objects.all())

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'username', 'is_active', 'is_staff', 'is_superuser',
                  'last_login', 'created_at', 'updated_at', 'profile', 'role', 'account_type')
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'last_login',
                            'created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        role = validated_data.pop('role')

        user = UserModel.objects.create_user(role=role, profile_data=profile_data, **validated_data)
        print(f"Sending registration email to {user.email}")
        EmailService.register(user)
        ProfileModel = apps.get_model('users', 'ProfileModel')
        if profile_data and not ProfileModel.objects.filter(user=user).exists():
            ProfileModel.objects.create(user=user, **profile_data)

        return user


class UpgradeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['account_type']

    def validate_account_type(self, value):
        if value != 'premium':
            raise serializers.ValidationError("Only upgrade to 'premium' is allowed.")
        return value

    def update(self, instance, validated_data):
        instance.account_type = validated_data['account_type']
        instance.is_upgrade_to_premium = True
        instance.save()
        return instance


class ManagerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)  # Профиль не обязателен
    role = serializers.PrimaryKeyRelatedField(queryset=UserRoleModel.objects.all(), default=3)

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'username', 'is_active', 'is_staff', 'is_superuser',
                  'last_login', 'created_at', 'updated_at', 'profile', 'role', 'account_type')
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'last_login',
                            'created_at', 'updated_at', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'default': True},
            'is_active': {'default': True}
        }

    @atomic
    def create(self, validated_data):
        UserModel = get_user_model()
        creator_user = self.context['request'].user

        if not (creator_user.is_superuser or (creator_user.is_staff and creator_user.role.name == 'admin')):
            raise serializers.ValidationError("Only superusers or admins can create managers")

        profile_data = validated_data.pop('profile', None)
        validated_data['is_staff'] = True  # Устанавливаем is_staff=True
        validated_data['is_active'] = True  # Устанавливаем is_active=True
        user = UserModel.objects.create_user(**validated_data)

        ProfileModel = apps.get_model('users', 'ProfileModel')
        if profile_data and not ProfileModel.objects.filter(user=user).exists():
            ProfileModel.objects.create(user=user, **profile_data)

        return user



class ProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModel
        fields = ('avatar',)

    def validate_avatar(self, avatar):
        max_size = 100 * 1024
        if avatar.size > max_size:
            raise serializers.ValidationError('max_size - 100kb')
        return avatar

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance

class BlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistModel
        fields = ['user', 'reason', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


