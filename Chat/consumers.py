import channels.exceptions
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncJsonWebsocketConsumer


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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        raise channels.exceptions.StopConsumer()

    async def receive_json(self, content):
        message = content["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message,
                "username": self.username
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            "message": event["message"],
            "username": event["username"]
        })