from django.db import models


class VkGroup(models.Model):
    """Database model for vk group."""

    group_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=264)
    users_count = models.BigIntegerField()

    def __str__(self):
        return f"{self.name} ({self.group_id})"
