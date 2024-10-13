from django.db import models
from django.conf import settings

from comments.utils import image_file


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    reply = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    home_page = models.URLField(blank=True, null=True)
    text = models.CharField(max_length=2084)
    image = models.ImageField(upload_to=image_file, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.text}"
