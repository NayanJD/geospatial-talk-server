from django.contrib import admin
from django.db import models
from rest_framework import serializers
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Polygon
from django.contrib.gis.admin import OSMGeoAdmin
from uuid import uuid4

class Factory(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField()

    geofence = gis_models.PolygonField()
    
    class Meta:
        db_table = "factories"

@admin.register(Factory)
class FactoryAdmin(OSMGeoAdmin):
    list_display = [
        "id",
        "name",
        "geofence"
    ]

class FactorySerializer(serializers.ModelSerializer):

    def validate_geofence(self, value):
        print(value)
        if not isinstance(value, Polygon):
            raise serializers.ValidationError("geofence should be a polygon")

        return value
    
    class Meta:
        model = Factory
        fields = "__all__"