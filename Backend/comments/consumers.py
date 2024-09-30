import json
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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    @database_sync_to_async
    def get_all_comments(self):
        comments = Comment.objects.filter(reply=None)
        return CommentListSerializer(comments, many=True).data

    async def send_comments_list(self):
        comments = await self.get_all_comments()
        await self.send(text_data=json.dumps({
            'action': 'list_comments',
            'comments': comments
        }))

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "create_comment":
            text = data.get("text")
            reply_id = data.get("reply")

            new_comment = await self.create_comment(text, reply_id)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'comment': new_comment
                }
            )

    @database_sync_to_async
    def create_comment(self, text, reply_id=None):
        comment = Comment.objects.create(
            user=self.scope['user'],  # Здесь нужно заменить на текущего пользователя
            text=text,
            reply_id=reply_id
        )
        return CommentListSerializer(comment).data

    async def chat_message(self, event):
        comment = event['comment']
        await self.send(text_data=json.dumps({
            'action': 'new_comment',
            'comment': comment
        }))
