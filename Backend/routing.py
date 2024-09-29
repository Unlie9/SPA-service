from django.urls import re_path
from comments.consumers import CommentConsumer
from user.consumers import UserConsumer


app_name = "comments"

websocket_urlpatterns = [
    re_path("ws/comments", CommentConsumer.as_asgi()),
]

urlpatterns = websocket_urlpatterns
