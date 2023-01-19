from django.core.management.base import BaseCommand

from vk_integration.tasks import update_vk_groups_task


class Command(BaseCommand):
    help = 'Run update_vk_groups task'

    def handle(self, *args, **options):
        result = update_vk_groups_task.apply_async()
        self.stdout.write(self.style.SUCCESS(f'Run update_vk_groups {str(result)}'))
