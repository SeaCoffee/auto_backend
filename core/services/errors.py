class ValidationErrors:
    """
    Класс для накопления и управления ошибками валидации.
    Позволяет добавлять ошибки, проверять их наличие и получать список всех ошибок.
    """
    def __init__(self):
        # Список для хранения ошибок
        self.errors = []

    def add_error(self, field, message):
        """
        Добавляет новую ошибку в список ошибок.
        :param field: Поле, к которому относится ошибка
        :param message: Сообщение об ошибке
        """
        self.errors.append({"field": field, "message": message})

    def has_errors(self):
        """
        Проверяет, есть ли ошибки.
        :return: True, если ошибки есть, иначе False
        """
        return len(self.errors) > 0

    def get_errors(self):
        """
        Возвращает список ошибок.
        :return: Список ошибок
        """
        return self.errors


class CustomValidationError(Exception):
    """
    Кастомное исключение для обработки ошибок валидации.
    Содержит сообщение об ошибке.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        """
        Возвращает строковое представление ошибки.
        :return: Сообщение ошибки
        """
        return self.message
