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

    def create(self, validated_data):
        factory = validated_data.pop("factory")

        factory_user = FactoryUser.objects.create(
            factory=factory, **validated_data
        )

        return factory_user


    class Meta: 
        model = FactoryUser
        fields = ["id", "user"]