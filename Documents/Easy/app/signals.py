from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()

@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created and not instance.is_staff and not instance.is_superuser:
        Customer.objects.create(user=instance)
