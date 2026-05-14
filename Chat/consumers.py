import channels.exceptions
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Message, Room


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        self.username = params.get('username', ['Anonymous'])[0]

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user.join",
                "username": self.username
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user.leave",
                "username": self.username
            }
        )
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        raise channels.exceptions.StopConsumer()

    async def receive_json(self, content):
        message = content["message"]

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message,
                "username": self.username
            }
        )

    @database_sync_to_async
    def save_message(self, message):
        room = Room.objects.get(name=self.room_name)
        Message.objects.create(
            room=room,
            username=self.username,
            content=message
        )

    async def chat_message(self, event):
        await self.send_json({
            "message": event["message"],
            "username": event["username"]
        })

    async def user_join(self, event):
        await self.send_json({
            "type": "join",
            "username": event["username"]
        })

    async def user_leave(self, event):
        await self.send_json({
            "type": "leave",
            "username": event["username"]
        })