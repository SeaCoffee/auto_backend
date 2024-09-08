from rest_framework_simplejwt.tokens import BlacklistMixin, Token
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
from core.enums.tokens_enum import ActionTokenEnum



class CustomToken(Token):
    """
    Кастомный токен, который добавляет дополнительную информацию о типе аккаунта пользователя.
    Наследуется от базового класса `Token`.
    """
    @classmethod
    def for_user(cls, user):
        """
        Создает токен для указанного пользователя и добавляет к нему тип аккаунта.
        :param user: Пользователь, для которого создается токен
        :return: Токен с добавленной информацией о типе аккаунта
        """
        token = super().for_user(user)
        token['account_type'] = user.account_type  # Добавляем тип аккаунта пользователя в токен
        return token


class ActivateToken(BlacklistMixin, CustomToken):
    """
    Токен для активации аккаунта. Наследуется от `CustomToken` и включает логику работы с черным списком.
    """
    token_type = ActionTokenEnum.ACTIVATE.token_type
    lifetime = ActionTokenEnum.ACTIVATE.lifetime


class RecoveryToken(BlacklistMixin, CustomToken):
    """
    Токен для восстановления пароля. Включает логику работы с черным списком.
    """
    token_type = ActionTokenEnum.RECOVERY.token_type
    lifetime = ActionTokenEnum.RECOVERY.lifetime


class AccessToken(BlacklistMixin, CustomToken):
    """
    Токен для доступа (обычно используется для аутентификации). Включает логику работы с черным списком.
    """
    token_type = ActionTokenEnum.ACCESS.token_type
    lifetime = ActionTokenEnum.ACCESS.lifetime


class SoketToken(CustomToken):
    """
    Токен для WebSocket-соединений. Наследуется от `CustomToken` и не работает с черным списком.
    С ЧС проблема с постоянным отключением.
    """
    token_type = ActionTokenEnum.SOCKET.token_type
    lifetime = ActionTokenEnum.SOCKET.lifetime

    def check_blacklist(self):
        """
        Метод проверки черного списка для WebSocket-токенов. Ничего не делает.
        """
        print("SoketToken blacklist method called, but it does nothing.")
        return


class JWTService:
    """
    Сервис для работы с JWT-токенами. Включает методы для создания, валидации и обновления токенов.
    """

    @staticmethod
    def create_token(user, token_class=ActivateToken):
        """
        Создает токен для пользователя с указанным классом токена.
        :param user: Пользователь, для которого создается токен
        :param token_class: Класс токена (по умолчанию `ActivateToken`)
        :return: Созданный токен
        """
        token = token_class.for_user(user)
        token['created_by'] = token_class.__name__  # Добавляем информацию о том, какой класс создал токен
        return token

    @staticmethod
    def validate_socket_token(token):
        """
        Валидация WebSocket-токена.
        :param token: Токен для валидации
        :return: Пользователь, связанный с токеном
        :raises ValueError: Если токен недействителен или пользователь не найден
        """
        UserModel = get_user_model()
        try:
            token_res = SoketToken(token)
            token_res.check_blacklist()  # Для WebSocket-токенов проверка черного списка не выполняется
            user_id = token_res.payload.get('user_id')
            if user_id is None:
                raise ValueError("Invalid token payload: 'user_id' is missing.")
            return get_object_or_404(UserModel, pk=user_id)
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    @staticmethod
    def validate_token(token, token_class):
        """
        Валидация любого токена (кроме WebSocket).
        :param token: Токен для валидации
        :param token_class: Класс токена для валидации
        :return: Пользователь, связанный с токеном
        :raises ValueError: Если токен недействителен или пользователь не найден
        """
        UserModel = get_user_model()
        try:
            token_res = token_class(token)
            token_res.check_blacklist()  # Проверяем, что токен не находится в черном списке

            if not isinstance(token_res, SoketToken):
                token_res.blacklist()  # Добавляем токен в черный список, если это не WebSocket-токен

            user_id = token_res.payload.get('user_id')
            if user_id is None:
                raise ValueError("Invalid token payload: 'user_id' is missing.")
            return get_object_or_404(UserModel, pk=user_id)
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    @staticmethod
    def update_user_account_type(user, new_type):
        """
        Обновляет тип аккаунта пользователя и создает новый токен с обновленными данными.
        :param user: Пользователь, чей аккаунт нужно обновить
        :param new_type: Новый тип аккаунта
        :return: Новый токен для пользователя
        """
        user.account_type = new_type  # Обновляем тип аккаунта
        user.save()  # Сохраняем изменения в базе данных
        return JWTService.create_token(user)  # Возвращаем новый токен для пользователя