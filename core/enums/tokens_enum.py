from enum import Enum
from datetime import timedelta


class ActionTokenEnum(Enum):
    ACTIVATE = ('activate', timedelta(days=30))
    RECOVERY = ('recovery', timedelta(days=20))
    ACCESS = ('access', timedelta(days=30))

# max lifetime for testing

    def __init__(self, token_type, lifetime):
        self.token_type = token_type
        self.lifetime = lifetime