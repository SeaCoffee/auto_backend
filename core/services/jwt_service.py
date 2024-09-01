from rest_framework_simplejwt.tokens import BlacklistMixin, Token
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
from core.enums.tokens_enum import ActionTokenEnum

import logging

logging.basicConfig(level=logging.DEBUG)

class CustomToken(Token):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['account_type'] = user.account_type
        return token

class ActivateToken(BlacklistMixin, CustomToken):
    token_type = ActionTokenEnum.ACTIVATE.token_type
    lifetime = ActionTokenEnum.ACTIVATE.lifetime

class RecoveryToken(BlacklistMixin, CustomToken):
    token_type = ActionTokenEnum.RECOVERY.token_type
    lifetime = ActionTokenEnum.RECOVERY.lifetime

class AccessToken(BlacklistMixin, CustomToken):
    token_type = ActionTokenEnum.ACCESS.token_type
    lifetime = ActionTokenEnum.ACCESS.lifetime

class SoketToken(CustomToken):
    token_type = ActionTokenEnum.SOKET.token_type
    lifetime = ActionTokenEnum.SOKET.lifetime

    def check_blacklist(self):
        print("SoketToken blacklist method called, but it does nothing.")
        return



class JWTService:
    @staticmethod
    def create_token(user, token_class=ActivateToken):
        token = token_class.for_user(user)
        token['created_by'] = token_class.__name__

        # Отладка
        print("Token Debug Info:")
        print(f"User ID: {user.id}")
        print(f"Account Type: {user.account_type}")
        print(f"Token: {token}")

        return token

    @staticmethod
    def validate_socket_token(token):
        UserModel = get_user_model()
        try:
            token_res = SoketToken(token)
            token_res.check_blacklist()
            user_id = token_res.payload.get('user_id')
            if user_id is None:
                raise ValueError("Invalid token payload: 'user_id' is missing.")
            return get_object_or_404(UserModel, pk=user_id)
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    @staticmethod
    def validate_token(token, token_class):
        UserModel = get_user_model()
        try:
            token_res = token_class(token)
            token_res.check_blacklist()

            # Проверка на тип токена. Если это SoketToken, не добавляем его в черный список.
            if not isinstance(token_res, SoketToken):
                token_res.blacklist()

            user_id = token_res.payload.get('user_id')
            if user_id is None:
                raise ValueError("Invalid token payload: 'user_id' is missing.")
            return get_object_or_404(UserModel, pk=user_id)
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    @staticmethod
    def update_user_account_type(user, new_type):
        user.account_type = new_type
        user.save()
        return JWTService.create_token(user)
