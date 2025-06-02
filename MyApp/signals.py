from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, Category, Payment
from django.core.mail import EmailMessage


@receiver(post_save, sender=Category)
def deactivate_products(sender, instance, **kwargs):
    if not instance.is_active:
        products = Product.objects.filter(categories=instance)
        products.update(is_active=False)
    
@receiver(post_save, sender=Payment)
def send_payment_email(sender, instance, created, **kwargs):
    if created:
        subject = "Payment Confirmation"
        message = f"Payment of Rs. {instance.amount} received for Order ID: {instance.order.id}"
        to_email = instance.order.customer_email
        EmailMessage(subject, message, to=[to_email]).send()


