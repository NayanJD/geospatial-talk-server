import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.contrib.gis.geos import Point

from demo.api.utils import getWebsocketResponseDict, getFactoryChannelGroupName
from demo.api.models import Factory

import logging

logger = logging.getLogger(__name__)


class FactoryConsumer(JsonWebsocketConsumer):
    groups = ["factory"]

    def connect(self):
        print(self.scope)
        self.factory_id = self.scope["url_route"]["kwargs"]["factory_id"]

        self.factory = Factory.objects.get(pk=self.factory_id)

        # self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        for group in self.groups:
            async_to_sync(self.channel_layer.group_add)(group, self.channel_name)

        self.accept()

    def disconnect(self, code):
        pass
        # Leave room group
        for group in self.groups:
            async_to_sync(self.channel_layer.group_add)(group, self.channel_name)

    # Receive message from WebSocket
    def receive_json(self, content):
        if not content:
            return

        print("content", content)

        if content.get("type", None) == "location_update":

            latitude = content["latitude"]

            longitude = content["longitude"]

            user_id = content["user_id"]

            # Send message to room group
            async_to_sync(self.channel_layer.send)(
                self.channel_name,
                {
                    "type": "location_update",
                    "latitude": latitude,
                    "longitude": longitude,
                    "user_id": user_id,
                },
            )
        else:
            self.send_json(("_", "Unknown type provided", False))

    # Receive message from room group
    def location_update(self, event):
        message = {}

        print("event", event)

        latitude = event["latitude"]
        longitude = event["longitude"]
        user_id = event["user_id"]

        is_inside = False
        if self.factory.geofence.contains(Point(latitude, longitude)):
            is_inside = True

        # Send message to WebSocket
        self.send_json(
            (
                "location_update",
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "user_id": user_id,
                    "is_inside": is_inside,
                },
                True,
            )
        )

    def decode_json(self, text_data):
        is_authenticated = True
        if not getattr(self, "user", None):
            is_authenticated = False

        try:
            return json.loads(text_data)
        except json.decoder.JSONDecodeError as e:
            logger.error(e)
            self.send_json(("_", "Bad json", False))
        except Exception as e:
            logger.error(e)
            self.send_json(("_", "Internal Error", False))

    def encode_json(self, content, **kwargs):
        is_authenticated = True
        if not getattr(self, "user", None):
            is_authenticated = False

        (type_name, content_data, is_success) = content

        return json.dumps(
            getWebsocketResponseDict(
                type_name, content_data, is_success, is_authenticated
            )
        )
