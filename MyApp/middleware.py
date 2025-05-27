# middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import CustomToken
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return  

        if auth_header.startswith("Token "):
            key = auth_header.split("Token ")[1]
        else:
            raise AuthenticationFailed("Invalid Authorization header format")

        try:
            token = CustomToken.objects.get(key=key)
        except CustomToken.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active or user is deleted")

        if not token.is_valid():
            raise AuthenticationFailed("Token has expired")

        request.user = token.user
        request.auth = token
