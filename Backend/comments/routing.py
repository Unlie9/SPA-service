from django.urls import path
from comments.consumers import CommentConsumer


app_name = "comments"

websocket_urlpatterns = [
    path("ws/comments", CommentConsumer.as_asgi()),
]
