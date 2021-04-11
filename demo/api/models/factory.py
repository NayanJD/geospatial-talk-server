from django.contrib import admin
from django.db import models
from rest_framework import serializers
from django.contrib.gis.db import models as gis_models
from uuid import uuid4

class Factory(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField()

    geofence = gis_models.PolygonField()