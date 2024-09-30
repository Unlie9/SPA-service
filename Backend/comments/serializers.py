from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    reply = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ("id", "replies", "user", "text", "created_at", "reply")
        read_only_fields = ("user",)

    @staticmethod
    def get_replies(obj):
        if isinstance(obj, Comment) and obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return None


class CommentListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    home_page = serializers.CharField(source="user.home_page", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        # TODO remove id
        fields = ("id", "username", "home_page", "created_at", "text", "replies")

    @staticmethod
    def get_replies(obj):
        if obj.replies.exists():
            return CommentListSerializer(obj.replies.all(), many=True).data
        return None
