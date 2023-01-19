from django.contrib import admin

from vk_integration.models import VkGroup


@admin.register(VkGroup)
class VkGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'users_count',
        'updated_at'
    )
