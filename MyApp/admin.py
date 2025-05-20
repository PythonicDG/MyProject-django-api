from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomUser, CustomGroup

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['first_name','username','phone_number','email']
    search_fields = ['username']
    list_filter = ['is_active']
    ordering = ['first_name']

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name','is_active','description']
    list_filter = ['is_active']
    ordering = ['name']
    search_fields = ['name']


admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(CustomGroup,GroupAdmin)