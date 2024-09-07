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
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message
