import sys
from io import BytesIO

from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers

from comments.models import Comment


class CommentListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    replies = serializers.SerializerMethodField()
    email = serializers.CharField(source="user.email", read_only=True)
    image = serializers.ImageField(required=False)


    class Meta:
        model = Comment
        fields = (
            "id",
            "username",
            "home_page",
            "created_at",
            "text",
            "replies",
            "email",
            "image"
            )

    @staticmethod
    def get_replies(obj):
        if obj.replies.exists():
            return CommentListSerializer(obj.replies.all(), many=True).data
        return []
    

    @staticmethod
    def validate_image(image):
        if image:
            try:
                img = Image.open(image)
                if img.format not in ["JPEG", "PNG", "GIF"]:
                    raise serializers.ValidationError("Invalid image type. Allowed types: JPG, PNG, GIF.")
            except IOError:
                raise serializers.ValidationError("Invalid file. Please upload a valid image.")
        
            max_width = 320
            max_height = 240
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                image_buffer = BytesIO()
                img_format = img.format if img.format else 'JPEG'
                img.save(image_buffer, format=img_format)
                image_buffer.seek(0)

                return InMemoryUploadedFile(
                    image_buffer,
                    None,  
                    f"{image.name.split('.')[0]}.{img_format.lower()}", 
                    f'image/{img_format.lower()}',
                    sys.getsizeof(image_buffer),
                    None
                )
        return image
