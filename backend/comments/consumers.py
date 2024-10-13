import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, Paginator
from django.db import transaction

from rest_framework.exceptions import ValidationError

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from comments.models import Comment
from comments.serializers import CommentListSerializer
from comments.utils import convert_base64_to_image


class CommentConsumer(AsyncWebsocketConsumer):
    SORTING = {
        "username": "user__username",
        "email": "user__email",
        "date": "created_at"
    }

    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
        else:
            self.room_name = "chat_room"
            self.current_sort_by = "date"
            self.current_sort_order = "desc"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            await self.send_comments_list()

    @database_sync_to_async
    def get_comments_from_db(self, page, page_size, sort_by, sort_order):
        sort = self.SORTING.get(sort_by, "created_at")
        order_prefix = '' if sort_order == 'asc' else '-'
        sort_field_with_order = f'{order_prefix}{sort}'

        paginator = Paginator(
            Comment.objects.filter(reply=None).select_related("user").order_by(sort_field_with_order),
            page_size
        )
        try:
            paginated_comments = paginator.get_page(page)
        except EmptyPage:
            paginated_comments = paginator.get_page(
                paginator.num_pages)
        return CommentListSerializer(paginated_comments, many=True).data, paginator.num_pages

    async def send_comments_list(self, page=1, page_size=25, sort_by="date", sort_order="desc"):
        comments, count_pages = await self.get_comments_from_db(page, page_size, sort_by, sort_order)
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
            image = data.get("image", None)

            if image:
                try:
                    image = await database_sync_to_async(convert_base64_to_image)(image)
                except ValidationError as e:
                    await self.send(text_data=json.dumps({"error": str(e)}))
                    return


            if data.get("action") == "list_comments":
                self.current_sort_by = data.get("sort_by", "date")
                self.current_sort_order = data.get("sort_order", "desc")
                await self.send_comments_list(
                    page=data.get("page", 1),
                    page_size=data.get("page_size", 25),
                    sort_by=self.current_sort_by,
                    sort_order=self.current_sort_order
                )

            elif data.get("action") == "create_comment":
                if text:
                    await self.create_comment(text, home_page, reply_id, image)
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            "type": "broadcast_comments",
                            "sort_by": self.current_sort_by,
                            "sort_order": self.current_sort_order,
                        }
                    )
                elif not text or text.strip() == "":
                    await self.send(text_data=json.dumps({
                        "error": "Comment text cannot be empty"
                    }))

    @staticmethod
    def create_comment_in_transaction(user, text, home_page, reply_comment=None, image=None):
        with transaction.atomic():
            Comment.objects.create(
                user=user,
                text=text,
                home_page=home_page,
                reply=reply_comment,
                image=image
            )

    async def create_comment(self, text, home_page=None, reply_id=None, image=None):
        user = self.scope["user"]
        if user.is_authenticated:
            try:
                reply_comment = None
                if reply_id:
                    reply_comment = await database_sync_to_async(
                        Comment.objects.get
                    )(pk=reply_id)

                await (database_sync_to_async(self.create_comment_in_transaction)
                       (user, text, home_page, reply_comment, image))

            except ObjectDoesNotExist:
                await self.send(text_data=json.dumps({
                    "error": "Comment not found"
                }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    "error": f"An error occurred while creating comment."
                }))

    async def broadcast_comments(self, event):
        await self.send_comments_list(
            page=1,
            page_size=25,
            sort_by=event.get("sort_by", "date"),
            sort_order=event.get("sort_order", "desc")
        )
