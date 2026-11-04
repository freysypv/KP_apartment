from django.conf import settings
from django.db import models


class Announcement(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False, help_text="Pinned announcements show first.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide without deleting.")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="announcements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title

