from django.urls import path, include
from rest_framework import routers
from comments.views import CommentViewSet


app_name = "comments"

router = routers.DefaultRouter()
router.register("", CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
