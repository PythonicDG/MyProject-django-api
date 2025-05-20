from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator

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