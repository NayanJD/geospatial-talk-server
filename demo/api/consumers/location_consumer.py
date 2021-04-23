import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import authenticate
from django.http import HttpRequest

from demo.api.utils import getWebsocketResponseDict, getFactoryChannelGroupName

import logging

logger = logging.getLogger(__name__)


class LocationConsumer(AsyncJsonWebsocketConsumer):
    # groups = ["factory"]

    # async def connect(self):
    #     # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
    #     # self.room_group_name = "chat_%s" % self.room_name

    #     # Join room group
    #     # async_to_sync(self.channel_layer.group_add)(
    #     #     self.room_group_name, self.channel_name
    #     # )

    #     await self.accept()

    async def disconnect(self, code):
        pass
        # Leave room group
        # for group in self.groups:
        # async_to_sync(self.channel_layer.group_discard)("factory", self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content):
        if not content:
            return

        if content.get("type", None) == "auth":
            # async_to_sync(self.channel_layer.send)(
            #     self.channel_name,
            #     content,
            # )

            await self.channel_layer.send(self.channel_name, content)

        else:
            if not getattr(self, "user", None):
                await self.send_json(("auth", {}, False))
                return

            if content.get("type", None) == "location_update":

                latitude = content["latitude"]

                longitude = content["longitude"]

                # Send message to room group
                # async_to_sync(self.channel_layer.send)(
                #     self.channel_name,
                #     {
                #         "type": "location_update",
                #         "latitude": latitude,
                #         "longitude": longitude,
                #     },
                # )

                await self.channel_layer.send(
                    self.channel_name,
                    {
                        "type": "location_update",
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )

                # async_to_sync(self.channel_layer.group_send)(
                #     "factory",
                #     {
                #         "type": "location_update",
                #         "latitude": latitude,
                #         "longitude": longitude,
                #         "user_id": self.user.id,
                #     },
                # )

                await self.channel_layer.group_send(
                    "factory",
                    {
                        "type": "location_update",
                        "latitude": latitude,
                        "longitude": longitude,
                        "user_id": self.user.id,
                    },
                )
            else:
                await self.send_json(("_", "Unknown type provided", False))

    # Receive message from room group
    async def location_update(self, event):
        message = {}

        message["latitude"] = event["latitude"]

        message["longitude"] = event["longitude"]

        # Send message to WebSocket
        await self.send_json(("location_update", message, True))

        # print(self.groups)

        # for group in self.groups:
        #     async_to_sync(self.channel_layer.group_send)(
        #         group,
        #         {
        #             "type": "location_update",
        #             "latitude": latitude,
        #             "longitude": longitude,
        #         },
        #     )

    async def auth(self, event):
        username = event["username"]
        password = event["password"]

        user = await sync_to_async(authenticate)(username=username, password=password)

        if user:
            self.user = user

            await self.send_json(("auth", "Success", True))

            factory_user = user.factories.all()

            # if factory_user:
            #     # self.groups.append(
            #     #     getFactoryChannelGroupName(factory_user[0].factory.id)
            #     # )

            #     # for group in self.groups:
            #     async_to_sync(self.channel_layer.group_add)(
            #         "factory",
            #         self.channel_name,
            #     )
        else:
            await self.send_json(("auth", "Bad bearer token", False))

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
