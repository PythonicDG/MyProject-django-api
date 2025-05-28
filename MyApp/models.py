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

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    categories = models.ManyToManyField(Category, related_name= 'products')

    def __str__(self):
        return self.name


    

    




