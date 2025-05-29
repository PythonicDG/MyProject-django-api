from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, Category

@receiver(post_save, sender=Category)
def deactivate_products(sender, instance, **kwargs):
    if not instance.is_active:
        products = Product.objects.filter(categories=instance)
        products.update(is_active=False)
    


