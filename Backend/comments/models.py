from django.db import models
from django.conf import settings


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    reply = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    # home_page = models.URLField(blank=True, null=True)
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.text[:20]}"
