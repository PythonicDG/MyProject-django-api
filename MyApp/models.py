from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token 
from django.utils import timezone
from datetime import timedelta



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

    def __str__(self):
        return self.username

class CustomGroup(Group):
    description = models.TextField(blank=True,null=True)
    is_active= models.BooleanField(default=True)

    def __str__(self):
        return self.name

# your_app/models.py
from django.db import models
from rest_framework.authtoken.models import Token
from django.conf import settings
import datetime

class CustomToken(Token):
    expiry_time = models.IntegerField(default=502)
    class Meta:
        verbose_name = "Custom Token"
        verbose_name_plural = "Custom Tokens"





   

