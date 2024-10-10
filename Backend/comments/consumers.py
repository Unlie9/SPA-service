import json
from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from comments.models import Comment
from comments.serializers import CommentListSerializer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
        else:
            self.room_name = "chat_room"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            await self.send_comments_list()

    @database_sync_to_async
    def get_comments_from_db(self, page, page_size):
        paginator = Paginator(
            Comment.objects.filter(reply=None).select_related("user"),
            page_size
        )
        try:
            paginated_comments = paginator.get_page(page)
        except EmptyPage:
            paginated_comments = paginator.get_page(
                paginator.num_pages)
        return CommentListSerializer(paginated_comments, many=True).data, paginator.num_pages

    async def send_comments_list(self, page=1, page_size=25):
        comments, count_pages = await self.get_comments_from_db(page, page_size)
        await self.send(text_data=json.dumps({
            "action": "list_comments",
            "comments": comments,
            "count_pages": count_pages,
            "current_page": page
        }))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            data = json.loads(text_data)
            text = data.get("text")
            home_page = data.get("home_page")
            reply_id = data.get("reply_id")
            if data.get("action") == "list_comments":
                page = data.get("page", 1)
                page_size = data.get("page_size", 25)
                await self.send_comments_list(page=page, page_size=page_size)

            elif data.get("action") == "create_comment":
                if text:
                    await self.create_comment(text, home_page, reply_id)
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            "type": "broadcast_comments"
                        }
                    )
                elif not text or text.strip() == "":
                    await self.send(text_data=json.dumps({
                        "error": "Comment text cannot be empty"
                    }))

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
                    "error": f"An error occurred while creating comment."
                }))
                print(f"Error while creating comment: {str(e)}")

    async def broadcast_comments(self, event):
        await self.send_comments_list(page=1, page_size=25)
