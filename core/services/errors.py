import json

class ValidationErrors:
    def __init__(self):
        self.errors = []

    def add_error(self, field, message):
        self.errors.append({"field": field, "message": message})

    def has_errors(self):
        return len(self.errors) > 0

    def get_errors(self):
        return self.errors



class CustomValidationError(Exception):
    def __init__(self, message, continue_logic=False):
        if isinstance(message, list):
            message = json.dumps(message)  # Сериализуем список в JSON-строку
        self.message = message
        self.continue_logic = continue_logic
        super().__init__(message)

    def __str__(self):
        return self.message

