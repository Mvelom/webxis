from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProfile


@receiver(post_save, sender=User)
def ensure_client_profile(sender, instance, created, **kwargs):
    if created:
        ClientProfile.objects.get_or_create(user=instance)
