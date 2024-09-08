from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

from core.services.jwt_service import JWTService, SoketToken


@database_sync_to_async
def get_user(token):
    """
    Асинхронная функция для получения пользователя по JWT-токену.
    Используется декоратор @database_sync_to_async, который преобразует синхронную работу с базой данных в асинхронную,
    чтобы использовать её в асинхронных веб-приложениях, таких как Channels.
    """
    try:
        # Валидируем токен через сервис JWT и получаем пользователя.
        user = JWTService.validate_socket_token(token)
        print(f"User validated: {user}")  # Выводим сообщение об успешной валидации пользователя.
        return user  # Возвращаем пользователя, если валидация прошла успешно.
    except Exception as e:
        # Если произошла ошибка при валидации токена, выводим сообщение об ошибке.
        print(f"Error validating token: {e}")
        return None  # Возвращаем None, если пользователь не был валидирован.


class AuthSocketMiddleware(BaseMiddleware):
    """
    Middleware для авторизации WebSocket соединений на основе JWT-токенов.
    Наследуется от BaseMiddleware и перехватывает запросы для авторизации пользователя.
    """

    async def __call__(self, scope, receive, send):
        """
        Основной метод для обработки каждого запроса. Проверяет наличие токена в query_string и валидирует пользователя.
        """
        # Получаем токен из query_string WebSocket соединения.
        token = (
            dict(
                [item.split('=') for item in scope['query_string'].decode('utf-8').split('&') if item]
            ).get('token', None)
        )
        # Если токен существует, валидируем его и сохраняем пользователя в scope['user']. Если токена нет, устанавливаем None.
        scope['user'] = await get_user(token) if token else None

        # Продолжаем выполнение цепочки запросов, вызывая метод родительского класса.
        return await super().__call__(scope, receive, send)


