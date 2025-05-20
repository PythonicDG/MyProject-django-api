from django.db import models
from django.contrib.auth.models import User, Group

class CustomUser(User):
    phone_number = models.CharField(max_length=15, blank= True,null=True)

    def __str__(self):
        return self.username

class CustomGroup(Group):
    description = models.TextField(blank=True,null=True)
    def __str__(self):
        return self.name