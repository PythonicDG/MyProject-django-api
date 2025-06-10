from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token 
from django.utils import timezone
from datetime import timedelta
import datetime

class CustomUser(User): 
    phone_number = models.CharField(max_length=13, 
                    blank= False,null=True,
                     validators=[
            RegexValidator(
                regex=r'^(\+91[\-\s]?|91[\-\s]?|0)?[6-9]\d{9}$', 
                message="Phone number must be entered in the format: +91....."
            )
        ]
    )
    class Meta:
        pass

    def __str__(self):
        return self.username

class CustomGroup(Group):
    description = models.TextField(blank=True,null=True)
    is_active= models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CustomToken(Token):
    expiry_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        pass

    def is_valid(self):
        return self.expiry_time and self.expiry_time > timezone.now()

    def save(self, *args, **kwargs):
        if not self.expiry_time:
            self.expiry_time = timezone.now() + timedelta(seconds=1000)
        super().save(*args, **kwargs)

class TempModel(models.Model):
    email = models.CharField(blank=False, max_length=30)
    otp = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
        
    def expiry_time(self):
        if self.otp and self.created_at:
            self.expiry_time = self.created_at + timedelta(seconds = 180)
            return self.expiry_time

class Cart(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name
        
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()

    def total_orders(self):
        return self.orders.filter(is_paid=True).count()

    def __str__(self):
        return self.customer_name



class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('preparing', 'Preparing'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=20)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def total_amount(self):
        return sum(item.qty * item.price for item in self.ordered_items.all())


    def __str__(self):
        return self.customer_name

class OrderedItem(models.Model):
    order = models.ForeignKey(Order, related_name='ordered_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"{self.qty} x {self.product.name}"

class Payment(models.Model):

    transaction_id = models.CharField(max_length=100, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.order.customer_name

    
class Storage(models.Model):
    file = models.FileField()

    def __str__(self):
        return self.file.path




        