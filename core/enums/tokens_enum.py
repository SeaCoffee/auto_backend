from enum import Enum
from datetime import timedelta


class ActionTokenEnum(Enum):
    """
    Перечисление токенов для различных действий, таких как активация аккаунта, восстановление пароля и доступ через сокет.
    Каждый токен имеет время жизни (lifetime).
    Max lifetime for testing!
    """
    ACTIVATE = ('activate', timedelta(days=30))
    RECOVERY = ('recovery', timedelta(days=30))
    ACCESS = ('access', timedelta(days=30))
    SOCKET = ('socket', timedelta(minutes=30))

    def __init__(self, token_type: str, lifetime: timedelta):
        """
        Инициализация токенов с типом действия и временем жизни.
        """
        self.token_type = token_type
        self.lifetime = lifetime
