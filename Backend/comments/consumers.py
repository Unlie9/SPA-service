import json
from asgiref.sync import sync_to_async
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
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

    async def send_comments_list(self):
        await self.send(text_data=json.dumps({
            "action": "list_comments",
            "comments": await self.get_comments_from_db(),
        }))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            data = json.loads(text_data)
            text = data.get("text")
            home_page = data.get("home_page")
            reply_id = data.get("reply_id")
            if data.get("action") == "create_comment":
                if text:
                    await self.create_comment(text, home_page, reply_id)
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            "type": "broadcast_comments"
                        }
                    )

    @staticmethod
    def create_comment_in_transaction(user, text, home_page, reply_comment=None):
        with transaction.atomic():
            Comment.objects.create(
                user=user,
                text=text,
                home_page=home_page,
                reply=reply_comment
            )

    async def create_comment(self, text, home_page=None, reply_id=None):
        user = self.scope["user"]
        if user.is_authenticated:
            try:
                reply_comment = None
                if reply_id:
                    reply_comment = await database_sync_to_async(
                        Comment.objects.get
                    )(pk=reply_id)

                await (database_sync_to_async(self.create_comment_in_transaction)
                       (user, text, home_page, reply_comment))

            except ObjectDoesNotExist:
                await self.send(text_data=json.dumps({
                    "error": "Comment not found"
                }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    "error": f"Error: {str(e)}"
                }))

    async def broadcast_comments(self, event):
        await self.send_comments_list()
