from django.db import models
from django.conf import settings
from rest_framework import serializers
from uuid import uuid4

class FactoryUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="factories", on_delete=models.CASCADE
    )

    factory = models.ForeignKey(
        "Factory",
        related_name="users",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "factory_users"

class FactoryUserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = FactoryUser
        fields = "__all__"