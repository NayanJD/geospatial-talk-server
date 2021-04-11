# Generated by Django 3.2 on 2021-04-11 06:42

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Factory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('geofence', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
        ),
    ]