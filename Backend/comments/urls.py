from django.urls import path, include
from rest_framework import routers
from comments.views import CommentView


app_name = "comments"

router = routers.DefaultRouter()
router.register("", CommentView)

urlpatterns = [
    path("", include(router.urls)),
]
