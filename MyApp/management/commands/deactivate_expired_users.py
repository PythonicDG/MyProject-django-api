from django.core.management.base import BaseCommand
from django.utils import timezone
from MyApp.models import CustomUser  # Use your actual app and model

class Command(BaseCommand):
    help = 'Deactivate users whose expiry_time has passed'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_users = CustomUser.objects.filter(
            expiry_time__lt=now,
            is_active=True
        )
        count = expired_users.update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"Deactivated {count} expired users."))
