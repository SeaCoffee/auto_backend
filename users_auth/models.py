from django.db import models
from core.models import BaseModel

class UserRoleModel(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=55)

    class Meta:
        db_table = 'role'