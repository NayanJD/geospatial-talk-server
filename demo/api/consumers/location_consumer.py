import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import authenticate
from django.http import HttpRequest

from demo.api.utils import getWebsocketResponseDict, getFactoryChannelGroupName

import logging

logger = logging.getLogger(__name__)


class LocationConsumer(JsonWebsocketConsumer):
    groups = []

    def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_group_name, self.channel_name
        # )

        self.accept()

    def disconnect(self):
        pass
        # Leave room group
        # async_to_sync(self.channel_layer.group_discard)(
        #     self.room_group_name, self.channel_name
        # )

    # Receive message from WebSocket
    def receive_json(self, content):
        if not content:
            return

        if content.get("type", None) == "auth":
            async_to_sync(self.channel_layer.send)(
                self.channel_name,
                content,
            )
        else:
            if not getattr(self, "user", None):
                self.send_json(("auth", {}, False))
                return

            if content.get("type", None) == "location_update":

                latitude = content["latitude"]

                longitude = content["longitude"]

                # Send message to room group
                async_to_sync(self.channel_layer.send)(
                    self.channel_name,
                    {
                        "type": "location_update",
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )
            else:
                self.send_json(("_", "Unknown type provided", False))

    # Receive message from room group
    def location_update(self, event):
        message = {}

        message["latitude"] = event["latitude"]

        message["longitude"] = event["longitude"]

        # Send message to WebSocket
        self.send_json(("location_update", message, True))

    def auth(self, event):
        username = event["username"]
        password = event["password"]

        user = authenticate(username=username, password=password)

        if user:
            self.user = user

            self.send_json(("auth", "Success", True))

            factory_user = user.factories.all()

            if factory_user:
                self.groups.append(
                    getFactoryChannelGroupName(factory_user[0].factory.id)
                )

                async_to_sync(self.channel_layer.group_add)(
                    getFactoryChannelGroupName(factory_user[0].factory.id),
                    self.channel_name,
                )
        else:
            self.send_json(("auth", "Bad bearer token", False))

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
