from django.db import transaction
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from comments.serializers import CommentSerializer, CommentListSerializer
from comments.models import Comment


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(reply__isnull=True)

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        reply_id = self.request.data.get("reply")
        with transaction.atomic():
            if reply_id:
                try:
                    comment_for_reply = Comment.objects.get(pk=reply_id)
                except Comment.DoesNotExist:
                    raise ValidationError({"detail": "Comment not found"})
                try:
                    serializer.save(user=self.request.user, reply=comment_for_reply)
                except Exception as e:
                    raise ValidationError({"detail": f"Error saving reply: {str(e)}"})
                else:
                    try:
                        serializer.save(user=self.request.user)
                    except Exception as e:
                        raise ValidationError({"detail": f"Error saving comment: {str(e)}"})

