from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomUser, CustomGroup, CustomToken, TempModel, Cart, Category, Product

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['first_name','username','phone_number','email']
    search_fields = ['groups']
    list_filter = ['is_active', 'groups']
    ordering = ['first_name']

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name','is_active','description']
    list_filter = ['is_active']
    ordering = ['name']
    search_fields = ['name']

class TokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'key',
        'created',
        'expiry_time'
    )

class TempAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'otp',
        'created_at',
        'expiry_time',
    )
    list_filter = ['email']
    search_fields = ['email']

class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'price'
    )
    list_filter = ['name']
    search_fields = ['name']

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_active'
    )

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_active'
    )

admin.site.register(CustomToken, TokenAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomGroup, GroupAdmin)
admin.site.register(TempModel, TempAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)