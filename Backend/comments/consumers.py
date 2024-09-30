import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from comments.models import Comment
from comments.serializers import CommentListSerializer


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
                    await self.send_comments_list()

    async def create_comment(self, text):
        user = self.scope["user"]

        if hasattr(user, '_wrapped') and not user._wrapped:
            user._setup()

        User = get_user_model()
        real_user = await database_sync_to_async(User.objects.get)(id=user.id)

        print(f"Текущий пользователь: {real_user}")

        await database_sync_to_async(Comment.objects.create)(
            user=real_user,
            text=text
        )

