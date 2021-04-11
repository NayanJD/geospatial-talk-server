from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):

    def create(self, *args, **kwargs):
        user = super().create(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        return user

    def update(self, *args, **kwargs):
        user = super().update(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        return user
        
    class Meta:
        model = User 
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "password",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["is_staff", "is_superuser",]
        extra_kwargs = {"password": {"write_only": True}}