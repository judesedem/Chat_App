import channels.exceptions
import json
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Message, Room


class ChatConsumer(AsyncJsonWebsocketConsumer):
    active_users = {}

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        self.username = params.get('username', ['Anonymous'])[0]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user.join", "username": self.username}
        )

        if self.room_name not in ChatConsumer.active_users:
            ChatConsumer.active_users[self.room_name] = set()
        ChatConsumer.active_users[self.room_name].add(self.username)

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user.leave", "username": self.username}
        )
        if self.room_name in ChatConsumer.active_users:
            ChatConsumer.active_users[self.room_name].discard(self.username)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        raise channels.exceptions.StopConsumer()

    async def receive_json(self, content):
        try:
            event_type = content.get("type")

            if not event_type:
                await self.send_json({"error": "missing type field"})
                return

            if event_type == "message":
                message = content.get("message")
                if not message:
                    await self.send_json({"error": "missing message field"})
                    return
                await self.save_message(message)
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "chat.message",
                        "message": message,
                        "username": self.username
                    }
                )

            elif event_type == "reaction":
                emoji = content.get("emoji")
                if not emoji:
                    await self.send_json({"error": "missing emoji field"})
                    return
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "chat.reaction",
                        "emoji": emoji,
                        "username": self.username
                    }
                )

            else:
                await self.send_json({"error": f"unknown event type: {event_type}"})

        except Exception as e:
            await self.send_json({"error": f"something went wrong: {str(e)}"})

    @database_sync_to_async
    def save_message(self, message):
        try:
            room, created = Room.objects.get_or_create(name=self.room_name)
            Message.objects.create(room=room, username=self.username, content=message)
        except Exception as e:
            print(f"Error saving message: {e}")

    async def chat_message(self, event):
        await self.send_json({
            "type": "message",
            "message": event["message"],
            "username": event["username"]
        })

    async def chat_reaction(self, event):
        await self.send_json({
            "type": "reaction",
            "emoji": event["emoji"],
            "username": event["username"]
        })

    async def user_join(self, event):
        await self.send_json({"type": "join", "username": event["username"]})

    async def user_leave(self, event):
        await self.send_json({"type": "leave", "username": event["username"]})

    async def receive(self, text_data=None, bytes_data=None):
        try:
            content = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_json({"error": "invalid JSON"})
            return
        
        try:
            await self.receive_json(content)
        except Exception as e:
            await self.send_json({"error": f"something went wrong: {str(e)}"})
            return