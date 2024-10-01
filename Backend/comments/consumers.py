import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

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
            Comment.objects.all(),
            many=True,
        ).data

    async def send_comments_list(self):
        print(await self.get_comments_from_db())
        await self.send(text_data=json.dumps({
            "action": "list_comments",
            "comments": await self.get_comments_from_db()
        }))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            data = json.loads(text_data)
            text = data.get("text")
            home_page = data.get("home_page")
            if data.get("action") == "create_comment":
                if text:
                    await self.create_comment(text, home_page)
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            "type": "broadcast_comments"
                        }
                    )
            elif data.get("action") == "reply_comment":
                reply_id = data.get("reply_id")
                if text:
                    await self.reply_comment(text, home_page, reply_id)
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

    async def reply_comment(self, text, home_page=None, reply_id=None):
        user = self.scope["user"]

        if user.is_authenticated:
            reply_comment = await database_sync_to_async(Comment.objects.get)(id=reply_id)

            await database_sync_to_async(Comment.objects.create)(
                user=user,
                text=text,
                home_page=home_page,
                reply=reply_comment
            )

    async def broadcast_comments(self, event):
        await self.send_comments_list()
