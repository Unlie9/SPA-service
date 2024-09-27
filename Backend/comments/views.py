from django.db import transaction
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets

from comments.serializers import CommentSerializer, CommentListSerializer
from comments.models import Comment


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [OrderingFilter]
    filterset_fields = ["user__username", "user__email", "created_at"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return self.queryset.filter(reply__isnull=True).order_by("-created_at")

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

