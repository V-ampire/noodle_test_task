from django.db import models


class VkGroup(models.Model):
    """Database model for vk group."""

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=264)
    users_count = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.id})"
