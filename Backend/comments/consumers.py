import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from comments.models import Comment
from comments.serializers import CommentListSerializer, CommentSerializer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "chat_room"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.send_comments_list()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    @database_sync_to_async
    def get_comments_from_db(self):
        return CommentListSerializer(
            Comment.objects.filter(reply=None),
            many=True,
        ).data

    async def send_comments_list(self):
        print(f"Отправляем комментарии: {await self.get_comments_from_db()}")
        await self.send(text_data=json.dumps({
            "action": "list_comments",
            "comments": await self.get_comments_from_db()
        }))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            data = json.loads(text_data)
            if data.get("action") == "create_comment":
                text = data.get("text")
                if text:
                    await self.create_comment(text)
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            "type": "broadcast_comments"
                        }
                    )

    async def create_comment(self, text, home_page=None):
        user = self.scope["user"]

        if user.is_authenticated:
            await database_sync_to_async(Comment.objects.create)(
                user=user,
                text=text,
                home_page=home_page
            )

    async def broadcast_comments(self, event):
        await self.send_comments_list()

