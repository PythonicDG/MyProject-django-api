# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User # Django's default User model

from .models import CustomUser, CustomGroup


class CustomUserInline(admin.StackedInline):
    model = CustomUser
    fields = ('phone_number',) 


class CustomUserAdmin(BaseUserAdmin):
    inlines = (CustomUserInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(CustomUser)


#Register Group models
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

admin.site.register(CustomGroup, CustomGroupAdmin)