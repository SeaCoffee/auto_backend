from django.db import models
from core.models import BaseModel

# Модель роли пользователя
class UserRoleModel(BaseModel):
    """
    Модель роли пользователя. Имеет уникальный идентификатор и название.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=55)

    class Meta:
        db_table = 'role'  # Имя таблицы в базе данных.
