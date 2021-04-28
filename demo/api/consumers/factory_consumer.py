import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.contrib.gis.geos import Point

from demo.api.utils import getWebsocketResponseDict, getFactoryChannelGroupName
from demo.api.models import Factory

import logging

logger = logging.getLogger(__name__)


class FactoryConsumer(AsyncJsonWebsocketConsumer):
    groups = ["factory"]
    factory = None

    async def connect(self):
        query_string = self.scope["query_string"]
        # print(type(query_string))
        # print(query_string.decode("utf-8").split("="))
        query_string_arr = query_string.decode("utf-8").split("=")

        if query_string_arr and query_string_arr[0] == "distance":
            self.distance = float(query_string_arr[1])

        if "factory_id" in self.scope["url_route"]["kwargs"]:
            self.factory_id = self.scope["url_route"]["kwargs"]["factory_id"]

            self.factory = await sync_to_async(Factory.objects.get)(pk=self.factory_id)

        # self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        pass
        # Leave room group
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content):
        if not content:
            return

        print("content", content)

        if content.get("type", None) == "location_update":

            latitude = content["latitude"]

            longitude = content["longitude"]

            user_id = content["user_id"]

            # Send message to room group
            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "location_update",
                    "latitude": latitude,
                    "longitude": longitude,
                    "user_id": user_id,
                },
            )
        else:
            await self.send_json(("_", "Unknown type provided", False))

    # Receive message from room group
    async def location_update(self, event):
        message = {}

        print("event", event)

        latitude = event["latitude"]
        longitude = event["longitude"]
        user_id = event["user_id"]

        is_inside = False

        point = Point(latitude, longitude, srid=4326)
        # print(self.distance)
        if getattr(self, "factory"):
            if not getattr(self, "distance", None):
                if self.factory.geofence.contains(point):
                    is_inside = True
            else:
                transformedFence = self.factory.geofence.transform(900913, clone=True)
                transformedPoint = point.transform(900913, clone=True)
                if transformedFence.distance(transformedPoint) <= self.distance:
                    is_inside = True

        # Send message to WebSocket
        await self.send_json(
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

    async def decode_json(self, text_data):
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

    async def encode_json(self, content, **kwargs):
        is_authenticated = True
        if not getattr(self, "user", None):
            is_authenticated = False

        (type_name, content_data, is_success) = content

        return json.dumps(
            getWebsocketResponseDict(
                type_name, content_data, is_success, is_authenticated
            )
        )
