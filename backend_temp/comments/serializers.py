from rest_framework import serializers

from comments.models import Comment


class CommentListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    replies = serializers.SerializerMethodField()
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "username", "home_page", "created_at", "text", "replies", "email")

    @staticmethod
    def get_replies(obj):
        if obj.replies.exists():
            return CommentListSerializer(obj.replies.all(), many=True).data
        return []
