from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomToken
from django.http import JsonResponse

class CustomTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return  

        if not auth_header.startswith("Token "):
            raise AuthenticationFailed("Invalid Authorization header format")

        key = auth_header.split("Token ")[1]

        try:
            token = CustomToken.objects.get(key=key)
            
        except CustomToken.DoesNotExist:
            return JsonResponse({"message":"Invalid Token"})
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            return JsonResponse({"message":"User is not active or has been deleted"})
            raise AuthenticationFailed("User is not active or has been deleted")

        if not token.is_valid():
            token.delete()  
            return JsonResponse({"message":"Token has Expired"})

        request.user = token.user
        request.auth = token
        
