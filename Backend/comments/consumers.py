import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from comments.models import Comment
from comments.serializers import CommentListSerializer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "chat_room"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.send_comments_list()

    @database_sync_to_async
    def get_comments_from_db(self):
        return CommentListSerializer(
            Comment.objects.filter(reply=None),
            many=True,
        ).data

    @database_sync_to_async
    def get_replies_from_db(self):
        return CommentListSerializer(
            Comment.objects.filter(reply__isnull=False),
            many=True
        ).data

    async def send_comments_list(self):
        if cache.get("comments_list"):
            await self.send(text_data=json.dumps({
                "action": "list_comments",
                "comments": cache.get("comments_list")
            }))
        else:
            cache.set(
                "comments_list",
                await self.get_comments_from_db(),
                timeout=300
            )

            await self.send(text_data=json.dumps({
                "action": "list_comments",
                "comments": await self.get_comments_from_db(),
            }))

    async def send_replies_list(self):
        if cache.get("replies_list"):
            await self.send(text_data=json.dumps({
                "action": "list_comments",
                "comments": cache.get("replies_list")
            }))
        else:
            cache.set(
                "replies_list",
                await self.get_replies_from_db(),
                timeout=300
            )

            await self.send(text_data=json.dumps({
                "action": "list_replies",
                "replies": await self.get_replies_from_db()
            }))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            data = json.loads(text_data)
            text = data.get("text")
            home_page = data.get("home_page")
            if data.get("action") == "create_comment":
                if text:
                    await self.create_comment(text, home_page)
                    cache.delete("comments_list")
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
                    cache.delete("replies_list")
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
        await self.send_replies_list()
